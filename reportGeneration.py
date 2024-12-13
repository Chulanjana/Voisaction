


# # Example usage
# # meeting_name = "Team Sync Meeting"
# # meeting_agenda = "Discuss quarterly objectives and assign tasks."
# # action_points = [["Assignddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd tasks", "Nuwan", "22.21.2014"], ["Review objddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddectives",  "Nuwan", "22.21.2014"]]
# # agenda_points = [["Discudddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddss Q1 objectives", "Yes","90%"], ["Assiddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddgn Q1 tasks", "No","90%"]]
# # similarity_scores = [["Alice", "90%"], ["Bob", "85%"], ["Charlie", "80%"]]
# # output_file = "meeting_summary.pdf"

# # create_meeting_pdf(meeting_name, meeting_agenda, action_points, agenda_points, similarity_scores, output_file)
# # print("PDF created successfully!")



from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def create_meeting_pdf(meeting_name, meeting_agenda, action_points, agenda_points, similarity_scores, transcription, output_file):
    # Define document
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    # Title
    title = Paragraph(f"<b>Meeting Summary: {meeting_name}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))  # Add some space

    # Meeting Agenda
    agenda_title = Paragraph("<b>Meeting Agenda:</b>", styles['Heading2'])
    elements.append(agenda_title)
    elements.append(Paragraph(meeting_agenda, styles['BodyText']))
    elements.append(Spacer(1, 12))

    # Action Points
    action_title = Paragraph("<b>Action Points:</b>", styles['Heading2'])
    elements.append(action_title)
    action_table_data = [["Action Point", "Assigned To", "Deadline"]]
    action_table_data.extend(
        [[Paragraph(cell, styles['BodyText']) for cell in row] for row in action_points]
    )
    action_table = Table(action_table_data, colWidths=[250, 150, 100])
    action_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(action_table)
    elements.append(Spacer(1, 12))

    # Agenda Points
    agenda_title = Paragraph("<b>Agenda Points:</b>", styles['Heading2'])
    elements.append(agenda_title)
    agenda_table_data = [["Agenda Point", "Covered (Yes/No)", "Percentage"]]
    agenda_table_data.extend(
        [[Paragraph(cell, styles['BodyText']) for cell in row] for row in agenda_points]
    )
    agenda_table = Table(agenda_table_data, colWidths=[350, 100, 100])
    agenda_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(agenda_table)
    elements.append(Spacer(1, 12))

    # Similarity Scores
    score_title = Paragraph("<b>Similarity Scores:</b>", styles['Heading2'])
    elements.append(score_title)
    score_table_data = [["Participant", "Similarity Score"]]
    score_table_data.extend(
        [[Paragraph(cell, styles['BodyText']) for cell in row] for row in similarity_scores]
    )
    score_table = Table(score_table_data, colWidths=[250, 150])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 12))

    # Meeting Transcription
    transcription_title = Paragraph("<b>Meeting Transcription:</b>", styles['Heading2'])
    elements.append(transcription_title)
    transcription_table_data = [["Speaker", "Transcript"]]
    transcription_table_data.extend(
        [[Paragraph(str(cell), styles['BodyText']) for cell in row] for row in transcription]
    )
    transcription_table = Table(transcription_table_data, colWidths=[150, 400])
    transcription_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(transcription_table)
    elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    print(f"PDF '{output_file}' created successfully!")





# transcription = [
#     ['Dinali', 'Must be 20. That is also not. That is definitely not'],
#     ['Madduranga', "cost at these two. When we ask, they say it's cost of"],
#     # Add other transcription rows here...
# ]

# create_meeting_pdf(
#     meeting_name="Project Update",
#     meeting_agenda="Discuss project updates and next steps.",
#     action_points=[
#         ["Update project timeline", "John Doe", "2024-11-30"],
#         ["Review budget allocation", "Jane Smith", "2024-12-05"]
#     ],
#     agenda_points=[
#         ["Project updates", "Yes", "100%"],
#         ["Budget review", "No", "50%"]
#     ],
#     similarity_scores=[
#         ["John Doe", "95%"],
#         ["Jane Smith", "88%"]
#     ],
#     transcription=transcription,
#     output_file="Meeting_Summary.pdf"
# )

