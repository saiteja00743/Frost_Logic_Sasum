"""Plain-language presentation with literal source values, not invented estimates."""
import re


PLAIN_RISKS = {
    "risk-indemnity": ("Who pays if someone makes a claim?", "This passage mentions paying for or defending against claims. Check who must pay and whether there is a limit.", "Check who is responsible and which costs are covered."),
    "risk-liability": ("Limits on compensation", "This passage discusses limits on what a party may have to pay if something goes wrong.", "Check the payment limit and any exceptions in the full clause."),
    "risk-auto-renew": ("Check whether the contract renews automatically", "This passage mentions renewal. Check when you must give notice if you do not want to continue.", "Confirm the renewal date, notice period and how notice must be sent."),
    "risk-termination": ("How can the agreement end?", "This passage mentions ending the agreement. It does not, by itself, establish a deadline for fixing a problem.", "Read the full termination section for reasons, notice requirements and any time allowed to fix a problem."),
    "risk-deposit-forfeit": ("Could you lose the deposit?", "This passage mentions keeping or losing a deposit. Check the conditions before relying on getting it back.", "Check when the deposit can be kept and how much can be deducted."),
    "risk-insurance": ("Check the insurance requirements", "This passage mentions required insurance. The amount and conditions need to be checked in the agreement.", "Compare the stated cover and conditions with your insurance policy."),
    "risk-non-solicit": ("Restrictions on hiring or contacting people", "This passage mentions restrictions on approaching employees or other people connected to the other party.", "Check who is covered and how long the restriction lasts."),
    "risk-survival": ("Duties that continue after the agreement ends", "This passage mentions duties that continue after the agreement ends.", "Check which duties continue and the time period stated in the full clause."),
    "risk-penalties": ("What happens if payment is late?", "This passage mentions charges or interest for late payment.", "Check the payment deadline, the stated charge and when it starts."),
}


def simplify_risks(analysis):
    for risk in analysis.get("risks", []):
        if risk.get("id") in PLAIN_RISKS:
            title, explanation, action = PLAIN_RISKS[risk["id"]]
            risk.update(title=title, explanation=explanation, recommended_action=action)
            if risk["id"] == "risk-termination":
                quote = risk.get("evidence", {}).get("quote", "")
                section = re.search(r"\bSection\s+([\d.]+)", quote, re.I)
                if section:
                    label = section.group(1).rstrip('.')
                    risk["explanation"] = f"This passage points to Section {label} for the rules on ending the agreement. Read that section to confirm any time allowed to fix a problem."
                    risk["recommended_action"] = f"Read Section {label} before deciding how or when the agreement can end."


def build_plain_summary(analysis, pages):
    money = []
    timing = []
    seen = set()
    patterns = [
        (money, r"(?:[$€£₹]\s*\d[\d,]*(?:\.\d+)?(?:\s*(?:million|billion|lakh|crore))?|\b(?:USD|INR|GBP|EUR|Rs\.?)\s*\d[\d,]*(?:\.\d+)?|\b\d+(?:\.\d+)?\s*%)"),
        (timing, r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b|\b\d{4}-\d{2}-\d{2}\b|\b(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fourteen|fifteen|twenty|thirty|forty|fifty|sixty|ninety)(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?\s+\()?\d+\)?\s+(?:(?:calendar|business)\s+)?(?:days?|months?|years?)\b"),
    ]
    for page in pages:
        text = re.sub(r"\s+", " ", page.get("text", "")).strip()
        for target, pattern in patterns:
            for match in re.finditer(pattern, text, re.I):
                # Keep each value with its source context; don't add amounts together
                # or label a rate/insurance limit as the total contract price.
                start = max(text.rfind('. ', 0, match.start()) + 2, 0)
                if start == 1:
                    start = 0
                end = text.find('. ', match.end())
                end = len(text) if end == -1 else end + 1
                start = max(start, match.start() - 100)
                end = min(end, match.end() + 160)
                quote = text[start:end].strip()
                value = match.group().strip()
                key = (page['page_number'], value, quote)
                if key in seen:
                    continue
                seen.add(key)
                lower = quote.lower()
                if target is money:
                    label = "Rate mentioned" if '%' in value else "Amount mentioned"
                    if "insurance" in lower or "coverage" in lower:
                        label = "Insurance amount"
                    elif "deposit" in lower:
                        label = "Deposit mentioned"
                    elif "subscription fee" in lower:
                        label = "Subscription fee"
                    elif '%' in value and ("late" in lower or "delinquent" in lower):
                        label = "Late-payment rate"
                else:
                    label = "Time period mentioned"
                    if "effective" in lower:
                        label = "Start date or term"
                    elif "non-renewal" in lower or "opt-out" in lower:
                        label = "Renewal term" if re.search(r"months?|years?", value, re.I) else "Renewal notice period"
                    elif "invoices" in lower or "payment" in lower:
                        label = "Payment timing"
                target.append({"label": label, "value": value, "evidence": {"page": page['page_number'], "quote": quote}})
    parties = [p['name'] for p in analysis.get('parties', [])]
    kind = analysis.get('contract_type', 'agreement')
    descriptions = {
        "Master Services Agreement (MSA)": "This agreement sets the rules for providing and paying for a service.",
        "Commercial Lease Agreement": "This agreement sets the rules for renting a business property.",
        "Non-Disclosure Agreement (NDA)": "This agreement sets rules for sharing and protecting private information.",
        "Software License Agreement": "This agreement sets the rules for using software.",
        "Employment Agreement": "This agreement sets the terms of a job.",
        "Vendor & Supply Agreement": "This agreement sets the rules for buying from a supplier.",
    }
    overview = descriptions.get(kind, "This document sets out an agreement between the parties.") + " "
    if parties:
        overview += "The parties identified are " + " and ".join(parties) + ". "
    overview += "Check the payment terms, important dates and rules for ending it before you act."
    issues = len(analysis.get('risks', []))
    return {
        "overview": overview,
        "result": f"{issues} items need a closer look." if issues else "No review items were detected. This does not mean the agreement is risk-free.",
        "money": money,
        "timing": timing,
        "next_steps": ["Check the amounts and dates against the source.", "Confirm the next deadline and choose who will handle it.", "Read any referenced sections before making a decision."],
        "notice": "Values below are copied from the document. They are not estimates or a total price.",
    }
