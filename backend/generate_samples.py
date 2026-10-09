import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

def create_sample_docs():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,
    )
    
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceBefore=4,
        spaceAfter=4,
    )

    # 1. CloudScale Enterprise SaaS MSA (4 pages)
    msa_file = SAMPLE_DIR / "CloudScale_Enterprise_SaaS_MSA.pdf"
    doc_msa = SimpleDocTemplate(str(msa_file), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story_msa = []

    # Page 1
    story_msa.append(Paragraph("MASTER SERVICES AGREEMENT", title_style))
    story_msa.append(Spacer(1, 15))
    story_msa.append(Paragraph(
        "This Master Services Agreement ('Agreement') is entered into and made effective as of <b>October 15, 2026</b> ('Effective Date'), "
        "by and between <b>CloudScale Technologies Inc.</b>, a Delaware corporation ('Provider'), and <b>Horizon Global Enterprises LLC</b>, "
        "a New York limited liability company ('Customer'). Provider and Customer may each be referred to as a 'Party' and collectively as the 'Parties'.",
        body_style
    ))
    story_msa.append(Paragraph("1. SUBSCRIPTION SERVICES & ACCESS", heading_style))
    story_msa.append(Paragraph(
        "1.1 Provision of Services. Provider hereby grants Customer a non-exclusive, non-transferable, worldwide right to access and use the CloudScale Enterprise Platform solely for Customer's internal business operations during the Term. Customer shall not sublicense, reverse engineer, or decompile any part of the software platform.",
        body_style
    ))
    story_msa.append(Paragraph("2. TERM AND AUTOMATIC RENEWAL", heading_style))
    story_msa.append(Paragraph(
        "2.1 Initial Term. The initial subscription term of this Agreement shall commence on the Effective Date and shall continue for a period of twelve (12) months ('Initial Term').",
        body_style
    ))
    story_msa.append(Paragraph(
        "2.2 Automatic Renewal. This Agreement shall automatically renew for successive periods of twelve (12) months unless either party provides written notice of non-renewal at least sixty (60) days prior to the expiration of the then-current term. Failure to deliver timely opt-out notice constitutes irrevocable consent to renewal at prevailing catalog rates.",
        body_style
    ))
    story_msa.append(PageBreak())

    # Page 2
    story_msa.append(Paragraph("MASTER SERVICES AGREEMENT (Continued)", title_style))
    story_msa.append(Spacer(1, 15))
    story_msa.append(Paragraph("3. FEES, INVOICING, AND PAYMENT TERMS", heading_style))
    story_msa.append(Paragraph(
        "3.1 Subscription Fees. Customer shall pay Provider the annual subscription fees in the amount of $120,000 USD, invoiced annually in advance. All invoices are due Net 30 days from date of receipt.",
        body_style
    ))
    story_msa.append(Paragraph(
        "3.2 Late Penalties. Any delinquent balance past thirty (30) days shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by law, whichever is less. In addition, Provider reserves the right to suspend platform access if invoices remain unpaid for more than forty-five (45) days.",
        body_style
    ))
    story_msa.append(Paragraph("4. SERVICE LEVEL AGREEMENT & UPTIME", heading_style))
    story_msa.append(Paragraph(
        "4.1 SLA Commitment. Provider shall use commercially reasonable efforts to maintain platform availability of 99.9% uptime during each calendar quarter, excluding scheduled maintenance windows announced at least 48 hours in advance.",
        body_style
    ))
    story_msa.append(PageBreak())

    # Page 3
    story_msa.append(Paragraph("MASTER SERVICES AGREEMENT (Continued)", title_style))
    story_msa.append(Spacer(1, 15))
    story_msa.append(Paragraph("5. INDEMNIFICATION", heading_style))
    story_msa.append(Paragraph(
        "5.1 Customer Indemnity. Customer agrees to defend, indemnify, and hold harmless Provider, its affiliates, directors, officers, and employees against any and all third-party claims, liabilities, damages, losses, and reasonable attorney fees arising out of or related to Customer Data, breach of acceptable use policies, or unauthorized access using Customer credentials.",
        body_style
    ))
    story_msa.append(Paragraph(
        "5.2 Procedure. Provider shall give Customer prompt written notice of any indemnifiable claim, and Customer shall have sole control over defense and settlement, provided that Customer shall not enter any settlement admitting liability without Provider's prior written approval.",
        body_style
    ))
    story_msa.append(Paragraph("6. CONFIDENTIALITY", heading_style))
    story_msa.append(Paragraph(
        "6.1 Protection. Each party agrees to protect the Confidential Information of the other party using the same degree of care it uses for its own proprietary information of like nature, but no less than reasonable care.",
        body_style
    ))
    story_msa.append(PageBreak())

    # Page 4
    story_msa.append(Paragraph("MASTER SERVICES AGREEMENT (Continued)", title_style))
    story_msa.append(Spacer(1, 15))
    story_msa.append(Paragraph("7. LIMITATION OF LIABILITY", heading_style))
    story_msa.append(Paragraph(
        "7.1 Cap on Liability. In no event shall Provider's total aggregate liability arising out of or related to this Agreement exceed the total subscription fees actually paid by Customer in the three (3) months immediately preceding the event giving rise to liability.",
        body_style
    ))
    story_msa.append(Paragraph(
        "7.2 Waiver of Consequential Damages. In no event shall either party be liable to the other for any indirect, incidental, punitive, special, or consequential damages, including loss of profits, data loss, or business interruption, regardless of the theory of liability.",
        body_style
    ))
    story_msa.append(Paragraph("8. GOVERNING LAW AND DISPUTE RESOLUTION", heading_style))
    story_msa.append(Paragraph(
        "8.1 Choice of Law. This Agreement shall be governed by the laws of the State of Delaware, without regard to conflict of law principles. Exclusive venue shall lie in the federal and state courts situated in New Castle County, Delaware.",
        body_style
    ))
    doc_msa.build(story_msa)

    # 2. Commercial Lease Agreement (3 pages)
    lease_file = SAMPLE_DIR / "MetroTower_Commercial_Office_Lease.pdf"
    doc_lease = SimpleDocTemplate(str(lease_file), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story_lease = []

    # Page 1
    story_lease.append(Paragraph("COMMERCIAL OFFICE LEASE AGREEMENT", title_style))
    story_lease.append(Spacer(1, 15))
    story_lease.append(Paragraph(
        "This Commercial Office Lease Agreement ('Lease') is entered into this <b>November 1, 2026</b>, "
        "by and between <b>MetroTower Properties REIT</b> ('Landlord') and <b>Nexus Media Labs Inc.</b> ('Tenant').",
        body_style
    ))
    story_lease.append(Paragraph("1. LEASED PREMISES", heading_style))
    story_lease.append(Paragraph(
        "1.1 Description. Landlord leases to Tenant Suite 1400 comprising approximately 4,200 rentable square feet located at 100 Financial Plaza, San Francisco, CA.",
        body_style
    ))
    story_lease.append(Paragraph("2. TERM AND RENT", heading_style))
    story_lease.append(Paragraph(
        "2.1 Lease Term. The term of this Lease shall be thirty-six (36) months commencing November 1, 2026 and terminating October 31, 2029.",
        body_style
    ))
    story_lease.append(Paragraph(
        "2.2 Monthly Base Rent. Tenant shall pay monthly base rent of $14,500.00 USD, payable in advance on or before the first (1st) day of each calendar month. Late payments past the 5th day shall incur a late charge of 5% of the overdue rent.",
        body_style
    ))
    story_lease.append(PageBreak())

    # Page 2
    story_lease.append(Paragraph("COMMERCIAL OFFICE LEASE (Continued)", title_style))
    story_lease.append(Spacer(1, 15))
    story_lease.append(Paragraph("3. SECURITY DEPOSIT AND FORFEITURE", heading_style))
    story_lease.append(Paragraph(
        "3.1 Security Deposit. Upon execution of this Lease, Tenant shall deposit with Landlord the sum of $29,000.00 USD as a security deposit for faithful performance of all obligations.",
        body_style
    ))
    story_lease.append(Paragraph(
        "3.2 Forfeiture on Default. In the event of any uncured material breach by Tenant, including default in payment lasting more than five (5) business days after notice, Landlord may retain and forfeit the entire security deposit as partial liquidated damages without prejudice to other remedies.",
        body_style
    ))
    story_lease.append(Paragraph("4. MAINTENANCE AND REPAIRS", heading_style))
    story_lease.append(Paragraph(
        "4.1 Tenant Obligations. Tenant shall keep and maintain the interior premises, plumbing fixtures, and dedicated HVAC units in good order, condition, and repair at Tenant's sole expense. Landlord shall maintain only common areas and exterior structural roof elements.",
        body_style
    ))
    story_lease.append(PageBreak())

    # Page 3
    story_lease.append(Paragraph("COMMERCIAL OFFICE LEASE (Continued)", title_style))
    story_lease.append(Spacer(1, 15))
    story_lease.append(Paragraph("5. INSURANCE AND INDEMNITY", heading_style))
    story_lease.append(Paragraph(
        "5.1 Commercial Liability Insurance. Tenant must maintain commercial general liability insurance with limits not less than $2,000,000 per occurrence, naming Landlord as an additional insured.",
        body_style
    ))
    story_lease.append(Paragraph("6. DEFAULT AND TERMINATION", heading_style))
    story_lease.append(Paragraph(
        "6.1 Termination for Cause. If Tenant fails to pay rent within ten (10) calendar days after written notice, Landlord may immediately terminate this Lease, re-enter the premises, and repossess the property.",
        body_style
    ))
    story_lease.append(Paragraph("7. GOVERNING LAW", heading_style))
    story_lease.append(Paragraph(
        "7.1 Jurisdiction. This Lease shall be construed under the laws of the State of California. Venue shall lie in San Francisco County.",
        body_style
    ))
    doc_lease.build(story_lease)

    # 3. Apex Innovations Mutual NDA (2 pages)
    nda_file = SAMPLE_DIR / "Apex_Innovations_Mutual_NDA.pdf"
    doc_nda = SimpleDocTemplate(str(nda_file), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story_nda = []

    # Page 1
    story_nda.append(Paragraph("MUTUAL NON-DISCLOSURE AGREEMENT", title_style))
    story_nda.append(Spacer(1, 15))
    story_nda.append(Paragraph(
        "This Mutual Non-Disclosure Agreement ('Agreement') is made effective as of <b>December 1, 2026</b>, "
        "by and between <b>Apex Innovations Corp</b>, a Massachusetts corporation, and <b>Quantum BioTech Systems Ltd</b>, "
        "a UK limited company. Each party may disclose or receive proprietary technical and commercial data for the purpose of "
        "evaluating a joint strategic product partnership ('Authorized Purpose').",
        body_style
    ))
    story_nda.append(Paragraph("1. CONFIDENTIAL INFORMATION", heading_style))
    story_nda.append(Paragraph(
        "1.1 Scope. 'Confidential Information' refers to any non-public technical data, source code, clinical test results, customer lists, and financial forecasts disclosed in oral or written form and marked as confidential.",
        body_style
    ))
    story_nda.append(Paragraph("2. OBLIGATIONS OF NON-DISCLOSURE", heading_style))
    story_nda.append(Paragraph(
        "2.1 Standard of Care. The receiving party agrees to hold all Confidential Information in strict confidence and not to disclose such information to any third party without prior written consent of the disclosing party.",
        body_style
    ))
    story_nda.append(PageBreak())

    # Page 2
    story_nda.append(Paragraph("MUTUAL NON-DISCLOSURE AGREEMENT (Continued)", title_style))
    story_nda.append(Spacer(1, 15))
    story_nda.append(Paragraph("3. SURVIVAL PERIOD AND RETURN OF MATERIALS", heading_style))
    story_nda.append(Paragraph(
        "3.1 Five-Year Survival. The obligations of confidentiality under this Agreement shall survive for five (5) years following the date of initial disclosure, except that trade secrets shall remain confidential indefinitely.",
        body_style
    ))
    story_nda.append(Paragraph(
        "3.2 Return or Destruction. Within fourteen (14) calendar days after receiving written request from the disclosing party, the receiving party shall return or certify destruction of all documents and tangible items containing Confidential Information.",
        body_style
    ))
    story_nda.append(Paragraph("4. NON-SOLICITATION", heading_style))
    story_nda.append(Paragraph(
        "4.1 Employee Covenant. For a period of twelve (12) months following the Effective Date, neither party shall solicit or induce any technical employee of the other party to terminate their employment.",
        body_style
    ))
    story_nda.append(Paragraph("5. GOVERNING LAW", heading_style))
    story_nda.append(Paragraph(
        "5.1 Jurisdiction. This Agreement shall be governed by the laws of the Commonwealth of Massachusetts.",
        body_style
    ))
    doc_nda.build(story_nda)

    print("Created sample PDF documents successfully.")

if __name__ == "__main__":
    create_sample_docs()
