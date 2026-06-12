#!/usr/bin/env python3
"""Converte um CSV em XLSX — sem precisar de Excel, pandas ou openpyxl.

Uso:
    python3 csv_para_xlsx.py entrada.csv [saida.xlsx]

Se 'saida.xlsx' for omitido, usa o mesmo nome do CSV com extensao .xlsx.
O XLSX gerado e lido normalmente pelo pandas.read_excel do ReFAIR.

Lembrete: o endpoint /storiesload exige uma coluna chamada exatamente
'User Story'. Garanta que o cabecalho do CSV tenha essa coluna.
"""
import sys, csv, html, zipfile


def _colname(i):
    s = ''
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def csv_para_xlsx(csv_path, xlsx_path):
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    if not rows:
        raise SystemExit('CSV vazio.')
    ncols = max(len(r) for r in rows)

    def is_num(v):
        s = str(v).strip()
        return s != '' and s.lstrip('-').replace('.', '', 1).isdigit()

    cells = []
    for ri, row in enumerate(rows, start=1):
        cxs = []
        for ci in range(ncols):
            val = row[ci] if ci < len(row) else ''
            ref = f'{_colname(ci)}{ri}'
            style = 1 if ri == 1 else 0
            if ri > 1 and is_num(val):
                cxs.append(f'<c r="{ref}" s="0"><v>{val}</v></c>')
            else:
                cxs.append(f'<c r="{ref}" s="{style}" t="inlineStr"><is>'
                           f'<t xml:space="preserve">{html.escape(str(val), quote=True)}'
                           f'</t></is></c>')
        cells.append(f'<row r="{ri}">' + ''.join(cxs) + '</row>')

    dim = f'A1:{_colname(ncols-1)}{len(rows)}'
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<dimension ref="{dim}"/>'
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        '</sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/>'
        '<sheetData>' + ''.join(cells) + '</sheetData>'
        f'<autoFilter ref="{dim}"/></worksheet>')

    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF305496"/></patternFill></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1">'
        '<alignment vertical="top" wrapText="1"/></xf>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyAlignment="1">'
        '<alignment horizontal="center" vertical="center"/></xf></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>')

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '</Types>')
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>')
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Stories" sheetId="1" r:id="rId1"/></sheets></workbook>')
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '</Relationships>')

    with zipfile.ZipFile(xlsx_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', root_rels)
        z.writestr('xl/workbook.xml', workbook)
        z.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        z.writestr('xl/styles.xml', styles)
        z.writestr('xl/worksheets/sheet1.xml', sheet)

    header = rows[0]
    print(f'OK -> {xlsx_path}  ({len(rows)-1} linhas, {ncols} colunas)')
    if 'User Story' not in header:
        print('  AVISO: nao ha coluna "User Story" — o /storiesload vai recusar.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.rsplit('.', 1)[0] + '.xlsx'
    csv_para_xlsx(inp, out)
