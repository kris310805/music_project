from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from django.utils import timezone

def generate_artists_pdf(artists):
    """Генерация PDF отчета по исполнителям"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Стили
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # center
    )
    
    # Заголовок
    title = Paragraph("Отчет по исполнителям", title_style)
    elements.append(title)
    
    # Дата генерации
    date_str = f"Сгенерировано: {timezone.now().strftime('%d.%m.%Y %H:%M')}"
    date_para = Paragraph(date_str, styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 10))
    
    # Таблица с данными
    data = [['Исполнитель', 'Кол-во релизов', 'Дата создания']]
    
    for artist in artists:
        data.append([
            artist.name,
            str(artist.releases.count()),
            artist.created_at.strftime('%d.%m.%Y')
        ])
    
    table = Table(data, colWidths=[200*mm, 60*mm, 60*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Генерация PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_tracks_pdf(tracks):
    """Генерация PDF отчета по трекам"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Заголовок
    title = Paragraph("Отчет по трекам", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Данные
    data = [['Трек', 'Исполнитель', 'Длительность', 'Статус']]
    
    for track in tracks:
        duration = f"{track.duration_seconds // 60}:{track.duration_seconds % 60:02d}"
        data.append([
            track.title,
            track.release.artist.name,
            duration,
            track.get_status_display()
        ])
    
    table = Table(data, colWidths=[180*mm, 100*mm, 50*mm, 60*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_release_pdf(release):
    """Генерация PDF для конкретного релиза"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Заголовок релиза
    title = Paragraph(f"Релиз: {release.title}", styles['Heading1'])
    elements.append(title)
    
    # Информация о релизе
    info_data = [
        ['Исполнитель:', release.artist.name],
        ['Год выпуска:', str(release.release_year)],
        ['Формат:', release.get_format_display()],
        ['Лейбл:', release.label.name if release.label else 'Не указан'],
        ['Дата создания:', release.created_at.strftime('%d.%m.%Y %H:%M')]
    ]
    
    info_table = Table(info_data, colWidths=[80*mm, 200*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    
    elements.append(Spacer(1, 10))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Треки релиза
    if release.tracks.exists():
        tracks_title = Paragraph("Треки в релизе:", styles['Heading2'])
        elements.append(tracks_title)
        
        tracks_data = [['Позиция', 'Название трека', 'Длительность']]
        for track in release.tracks.all():
            duration = f"{track.duration_seconds // 60}:{track.duration_seconds % 60:02d}"
            tracks_data.append([
                track.position or '-',
                track.title,
                duration
            ])
        
        tracks_table = Table(tracks_data, colWidths=[50*mm, 150*mm, 50*mm])
        tracks_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(tracks_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer