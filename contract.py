import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from bidi.algorithm import get_display
import arabic_reshaper

# تسجيل الخط العربي
font_path = "Amiri-Regular.ttf"
pdfmetrics.registerFont(TTFont('Arabic', font_path))

def reshape_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def format_date(date_val):
    if pd.isna(date_val):
        return ""
    try:
        return pd.to_datetime(date_val).strftime("%d/%m/%Y")
    except:
        return str(date_val)

def generate_contract_pdf(group_name, df_group):
    filename = f"عقود تجديد الموظفين - {group_name}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_normal.fontName = "Arabic"
    style_normal.fontSize = 10
    style_normal.leading = 14

    # عنوان المستند
    header_text = f"عقود تجديد الموظفين - الإدارة: {group_name[0]} - المنطقة: {group_name[2]} - الفرع: {group_name[1]}"
    header = Paragraph(reshape_arabic_text(header_text), style_normal)
    elements.append(header)
    elements.append(Spacer(1, 12))

    # رؤوس الأعمدة
    column_headers = [
        "اسم الموظف",
        "الوظيفة",
        "تاريخ التعيين",
        "تاريخ انتهاء العقد",
        "الراتب",
        "☐ المدير المباشر",
        "☐ الموارد البشرية",
        "☐ مدير المنطقة"
    ]
    columns_display = [reshape_arabic_text(col) for col in column_headers]
    data = [columns_display]

    for _, row in df_group.iterrows():
        salary = row['الراتب']
        if pd.isna(salary):
            salary_str = ""
        else:
            salary_str = f"{float(salary):.2f}" if not float(salary).is_integer() else str(int(salary))

        values = [
            reshape_arabic_text(row['اسم الموظف']),
            reshape_arabic_text(row['الوظيفة']),
            reshape_arabic_text(format_date(row['تاريخ التعيين'])),
            reshape_arabic_text(format_date(row['تاريخ انتهاء العقد'])),
            reshape_arabic_text(salary_str),
            "", "", ""
        ]
        data.append(values)

    col_widths = [100, 100, 80, 80, 60, 80, 90, 90]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))

    # توقيعات المدراء على سطر واحد بتوزيع مناسب
    signatures = [
        Paragraph(reshape_arabic_text("توقيع المدير المباشر"), style_normal),
        Paragraph(reshape_arabic_text("توقيع مدير الموارد البشرية"), style_normal),
        Paragraph(reshape_arabic_text("توقيع مدير المنطقة"), style_normal),
    ]
    signature_table = Table([signatures], colWidths=[200, 200, 200])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
    ]))
    elements.append(signature_table)

    elements.append(PageBreak())
    doc.build(elements)
    print(f"تم إنشاء ملف PDF: {filename}")

if __name__ == "__main__":
    df = pd.read_excel("DATA.xlsx")
    grouping_cols = ['الاداره', 'الفرع', 'المنطقة']
    grouped = df.groupby(grouping_cols)

    for group_name, group_df in grouped:
        generate_contract_pdf(group_name, group_df.reset_index(drop=True))
