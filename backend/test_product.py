"""Offline product regression suite; never reads deployment secrets or customer data."""
import os
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

_test_dir = tempfile.TemporaryDirectory(prefix="clauseguard-tests-")
os.environ["DATA_DIR"] = _test_dir.name
os.environ["ALLOW_DEMO"] = "true"
os.environ["DEMO_SESSION_SECRET"] = "test-only-demo-secret-that-is-not-used-in-production"
for key in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET", "GROQ_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY"):
    os.environ[key] = ""

from fastapi.testclient import TestClient
from jose import jwt
from app.main import app
from app.database import db
from app.auth.deps import _decode_token
from app.services.workspace_service import deliver_reminders, connect
from app.services.verification_service import VerificationService
from app.services.analysis_service import AnalysisService


class ProductTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def setUp(self):
        self.a = {"Authorization": "Bearer " + self.client.post("/api/session/demo").json()["access_token"]}
        self.b = {"Authorization": "Bearer " + self.client.post("/api/session/demo").json()["access_token"]}
        self.uid = _decode_token(self.a["Authorization"].split()[1])["sub"]
        self.doc = "doc-" + self.uid
        self.analysis_id = "analysis-" + self.uid
        db.save_document(self.doc, "Vendor agreement.pdf", 1, 100, 25, "test.pdf",
                         [{"page_number": 1, "text": "Notice is due 60 days before renewal.", "word_count": 7}], self.uid)
        db.save_analysis(self.analysis_id, self.doc, {
            "document_id": self.doc, "document_name": "Vendor agreement.pdf", "risks": [],
            "deadlines": [{"id": "dl-1", "title": "Renewal notice", "date_or_trigger": "60 days before renewal",
                           "evidence": {"quote": "Notice is due 60 days before renewal.", "page": 1}, "verification_status": "verified"}],
        }, "test", self.uid)

    def payload(self, **changes):
        result = {"document_id": self.doc, "title": "Confirm vendor renewal", "owner": "Priya · Operations",
                  "due_date": (date.today() + timedelta(days=5)).isoformat(), "timezone": "Asia/Kolkata",
                  "confirmed": True, "notes": "Review vendor notice delivery requirements."}
        result.update(changes)
        return result

    def create(self, **changes):
        response = self.client.post("/api/actions", headers=self.a, json=self.payload(**changes))
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_auth_rejects_forgery_and_old_guest_header(self):
        self.assertEqual(self.client.get("/api/workspace", headers={"X-Guest-ID": self.uid}).status_code, 401)
        forged = jwt.encode({"sub": self.uid, "aud": "authenticated", "exp": 9999999999}, "attacker", algorithm="HS256")
        self.assertEqual(self.client.get("/api/workspace", headers={"Authorization": "Bearer " + forged}).status_code, 401)
        with patch.dict(os.environ, {"ALLOW_DEMO": "false"}):
            self.assertEqual(self.client.post("/api/session/demo").status_code, 403)
            self.assertEqual(self.client.get("/api/workspace", headers=self.a).status_code, 401)

    def test_cross_user_reads_and_writes_are_blocked(self):
        action = self.create()
        for path in (f"/api/documents/{self.doc}", f"/api/analyses/{self.analysis_id}",
                     f"/api/analyses/{self.analysis_id}/report", f"/api/actions/{action['id']}/events",
                     f"/api/actions/{action['id']}/calendar"):
            self.assertEqual(self.client.get(path, headers=self.b).status_code, 404, path)
        self.assertEqual(self.client.post("/api/actions", headers=self.b, json=self.payload()).status_code, 404)
        self.assertEqual(self.client.patch(f"/api/actions/{action['id']}/status", headers=self.b,
                         json={"status": "completed", "version": 1, "note": "Attempted completion"}).status_code, 404)
        self.assertEqual(self.client.get("/api/workspace", headers=self.b).json()["contracts"], [])

    def test_authenticated_tokens_require_signature_expiry_issuer_and_audience(self):
        secret = 'test-only-supabase-secret'
        claims = {'sub': 'real-user', 'aud': 'authenticated', 'iss': 'https://example.supabase.co/auth/v1', 'exp': 9999999999}
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://example.supabase.co', 'SUPABASE_JWT_SECRET': secret}):
            self.assertEqual(_decode_token(jwt.encode(claims, secret, algorithm='HS256'))['sub'], 'real-user')
            self.assertIsNone(_decode_token(jwt.encode(claims, 'wrong-secret', algorithm='HS256')))
            for changes in ({'exp': 1}, {'aud': 'other-app'}, {'iss': 'https://wrong.example'}):
                self.assertIsNone(_decode_token(jwt.encode({**claims, **changes}, secret, algorithm='HS256')))

    def test_rescheduling_retires_old_inbox_and_delivers_new_schedule(self):
        due = (date.today() + timedelta(days=1)).isoformat()
        action = self.create(due_date=due, timezone='UTC')
        before = self.client.get('/api/workspace', headers=self.a).json()
        self.assertEqual(len(before['reminders']), 1)
        payload = self.payload(due_date=(date.today() + timedelta(days=60)).isoformat(), timezone='UTC')
        payload.pop('document_id')
        payload['version'] = 1
        updated = self.client.put(f"/api/actions/{action['id']}", headers=self.a, json=payload)
        self.assertEqual(updated.json()['schedule_version'], 2)
        self.assertEqual(self.client.get('/api/workspace', headers=self.a).json()['reminders'], [])

    def test_failed_document_storage_does_not_report_success(self):
        sample = Path(__file__).parent.parent / 'sample_documents' / 'CloudScale_Enterprise_SaaS_MSA.pdf'
        with patch('app.routes.documents.save_document', side_effect=RuntimeError('storage unavailable')):
            result = self.client.post('/api/documents', headers=self.a, files={'file': ('Vendor.pdf', sample.read_bytes(), 'application/pdf')})
        self.assertEqual(result.status_code, 503)

    def test_date_confirmation_validation(self):
        for changes in ({"confirmed": False}, {"owner": " "}, {"due_date": "not-a-date"},
                        {"timezone": "not/a-zone"}, {"notice_days": 60},
                        {"renewal_date": "2027-01-01", "notice_days": 60, "due_date": "2026-12-01"}):
            self.assertEqual(self.client.post("/api/actions", headers=self.a, json=self.payload(**changes)).status_code, 422, str(changes))
        action = self.create(renewal_date="2027-01-01", notice_days=60, due_date="2026-11-02")
        self.assertEqual(action["due_date"], "2026-11-02")

    def test_source_is_server_owned_and_unique(self):
        action = self.create(analysis_id=self.analysis_id, deadline_id="dl-1")
        self.assertEqual(action["source"]["evidence"]["quote"], "Notice is due 60 days before renewal.")
        duplicate = self.client.post("/api/actions", headers=self.a, json=self.payload(analysis_id=self.analysis_id, deadline_id="dl-1"))
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(self.client.post("/api/actions", headers=self.a, json=self.payload(source={"quote": "invented"})).status_code, 422)

    def test_action_lifecycle_and_optimistic_lock(self):
        action = self.create()
        payload = self.payload(title="Send cancellation notice")
        payload.pop("document_id")
        payload["version"] = 1
        response = self.client.put(f"/api/actions/{action['id']}", headers=self.a, json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.put(f"/api/actions/{action['id']}", headers=self.a, json=payload).status_code, 409)
        done = self.client.patch(f"/api/actions/{action['id']}/status", headers=self.a,
                                json={"version": 2, "status": "completed", "note": "Notice sent; email reference CG-142"})
        self.assertEqual(done.status_code, 200, done.text)
        self.assertEqual(self.client.get(f"/api/actions/{action['id']}/calendar", headers=self.a).status_code, 409)
        events = self.client.get(f"/api/actions/{action['id']}/events", headers=self.a).json()
        self.assertEqual([e["kind"] for e in events], ["completed", "updated", "confirmed"])
        reopened = self.client.patch(f"/api/actions/{action['id']}/status", headers=self.a,
                                    json={"version": 3, "status": "open", "note": "Vendor needs a corrected notice"})
        self.assertEqual(reopened.json()["schedule_version"], 2)

    def test_reminders_deduplicate_catch_up_and_stop_after_completion(self):
        action = self.create(due_date="2027-01-08", timezone="Asia/Kolkata")
        tick = datetime(2027, 1, 1, 0, 0, tzinfo=timezone.utc)
        deliver_reminders(self.uid, tick)
        deliver_reminders(self.uid, tick)
        with connect() as conn:
            rows = conn.execute("SELECT * FROM action_reminders WHERE action_id=?", (action["id"],)).fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["milestone"], 7)
            reminder_id = rows[0]["id"]
        self.assertEqual(self.client.patch(f"/api/reminders/{reminder_id}/read", headers=self.b).status_code, 404)
        self.assertEqual(self.client.patch(f"/api/reminders/{reminder_id}/read", headers=self.a).status_code, 200)
        # UTC Jan 7 is already Jan 8 in Kolkata: due-day reminder.
        deliver_reminders(self.uid, datetime(2027, 1, 7, 20, tzinfo=timezone.utc))
        with connect() as conn:
            milestones = [r[0] for r in conn.execute("SELECT milestone FROM action_reminders WHERE action_id=?", (action["id"],))]
            self.assertEqual(sorted(milestones), [0, 7])
        self.client.patch(f"/api/actions/{action['id']}/status", headers=self.a,
                          json={"version": 1, "status": "completed", "note": "Completed before deadline"})
        deliver_reminders(self.uid, datetime(2027, 2, 1, tzinfo=timezone.utc))
        with connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM action_reminders WHERE action_id=?", (action["id"],)).fetchone()[0], 2)

    def test_calendar_escaping_and_line_folding(self):
        action = self.create(title="Renewal; ACME, India", notes="Long context " + "é" * 150 + "\nSecond line")
        response = self.client.get(f"/api/actions/{action['id']}/calendar", headers=self.a)
        self.assertEqual(response.status_code, 200)
        self.assertIn("SUMMARY:Renewal\\; ACME\\, India", response.text)
        self.assertIn("TRIGGER:-P30D", response.text)
        self.assertIn("TRIGGER:-P0D", response.text)
        self.assertTrue(all(len(line.encode('utf-8')) <= 75 for line in response.text.split('\r\n')))

    def test_quote_negation_never_verifies(self):
        text = "The customer shall not be liable for any indirect or consequential damages arising under this agreement."
        quote = text.replace("shall not", "shall")
        status, _, _, _ = VerificationService.verify_quote(quote, 1, [{"page_number": 1, "text": text}])
        self.assertEqual(status, "needs_review")
        self.assertEqual(VerificationService.verify_quote(text, 1, [{"page_number": 1, "text": text}])[0], "verified")

    def test_simple_summary_uses_actual_values_and_no_invented_cure_period(self):
        from app.services.plain_summary_service import build_plain_summary, simplify_risks
        analysis = {'risks': [{'id': 'risk-termination', 'evidence': {
            'quote': 'terminate this Agreement in accordance with Section 4 of this Agreement.'}}]}
        simplify_risks(analysis)
        risk = analysis['risks'][0]
        self.assertIn('Section 4', risk['explanation'])
        self.assertNotIn('30', risk['recommended_action'])
        pages = [{'page_number': 2, 'text': 'Customer pays $4,500 annually. Payment is due within 14 days. Late interest is 1.5% per month.'}]
        summary = build_plain_summary(analysis, pages)
        self.assertEqual([m['value'] for m in summary['money']], ['$4,500', '1.5%'])
        self.assertTrue(any('14 days' in t['value'] for t in summary['timing']))
        self.assertEqual(build_plain_summary({}, [{'page_number': 1, 'text': 'See the payment schedule.'}])['money'], [])
        for item in summary['money'] + summary['timing']:
            self.assertIn(item['value'], item['evidence']['quote'])

    def test_upload_analyze_confirm_and_export(self):
        sample = Path(__file__).parent.parent / 'sample_documents' / 'CloudScale_Enterprise_SaaS_MSA.pdf'
        response = self.client.post('/api/documents', headers=self.a, files={'file': ('Vendor.pdf', sample.read_bytes(), 'application/pdf')})
        self.assertEqual(response.status_code, 200, response.text)
        doc_id = response.json()['document_id']
        response = self.client.post('/api/analyze', headers=self.a, json={'document_id': doc_id})
        self.assertEqual(response.status_code, 200, response.text)
        analysis = response.json()
        self.assertEqual(analysis['coverage'], {'processed_pages': 4, 'total_pages': 4})
        self.assertGreaterEqual(analysis['analysis_seconds'], 0)
        self.assertIn('plain_summary', analysis)
        self.assertTrue(analysis['deadlines'])
        self.assertTrue(any('sixty (60)' in d['date_or_trigger'] for d in analysis['deadlines']))
        action = self.create(document_id=doc_id, analysis_id=analysis['analysis_id'], deadline_id=analysis['deadlines'][0]['id'])
        self.assertEqual(action['document_name'], 'Vendor.pdf')
        report = self.client.get(f"/api/analyses/{analysis['analysis_id']}/report", headers=self.a)
        self.assertEqual(report.status_code, 200, report.text[:100] if report.status_code != 200 else '')
        self.assertTrue(report.content.startswith(b'%PDF'))
        workspace = self.client.get('/api/workspace', headers=self.a).json()
        self.assertTrue(any(c['id'] == doc_id for c in workspace['contracts']))
        self.assertTrue(any(a['id'] == action['id'] for a in workspace['actions']))

    def test_long_contract_page_coverage(self):
        # Exercise the actual request builder without sending a document to an external provider.
        import asyncio
        from unittest.mock import AsyncMock
        pages = [{'page_number': n, 'text': f'Unique page {n} clause.', 'word_count': 4} for n in range(1, 26)]
        response = unittest.mock.Mock(status_code=200)
        response.json.return_value = {'choices': [{'message': {'content': '{}'}}]}
        client = AsyncMock()
        client.post.return_value = response
        with patch('app.services.analysis_service.httpx.AsyncClient') as factory:
            factory.return_value.__aenter__.return_value = client
            asyncio.run(AnalysisService._analyze_with_llm(pages, 'sk-test-offline', 'openai', None))
        sent = client.post.call_args.kwargs['json']['messages'][1]['content']
        self.assertIn('Unique page 25 clause.', sent)


if __name__ == '__main__':
    unittest.main(verbosity=2)
