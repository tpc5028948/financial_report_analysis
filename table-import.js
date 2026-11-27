/* Offline, dependency-free CSV / XLSX reader and single-period financial field mapper. */
(function () {
  'use strict';

  const MiB = 1024 * 1024;
  const LIMIT = { file: 8 * MiB, xml: 4 * MiB, expanded: 32 * MiB,
    parts: 256, sheets: 16, rows: 5000, columns: 128, cells: 75000, text: 4096 };
  const TOO_LARGE = '表格超出离线导入上限，请仅保留需要的工作表、行和列后重试。';
  const BAD_ZIP = 'XLSX 文件损坏，或使用了不支持的 ZIP 格式。';
  const NOT_XLSX = '文件不是普通的 XLSX 工作簿；不支持 XLS、XLSM、PDF 或其他文件改名导入。';
  const BAD_XML = 'XLSX 工作簿内部格式无效。';
  const sourceLines = new WeakMap();

  function check(ok, message) {
    if (!ok) throw new Error(message);
  }

  function decodeCsv(bytes) {
    const utf8Bom = bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf;
    check(!(bytes[0] === 0xff && bytes[1] === 0xfe) && !(bytes[0] === 0xfe && bytes[1] === 0xff),
      'CSV 请保存为 UTF-8 或 GB18030 编码。');
    try { return new TextDecoder('utf-8', { fatal: true }).decode(bytes); }
    catch (_) {
      if (!utf8Bom) {
        try { return new TextDecoder('gb18030', { fatal: true }).decode(bytes); } catch (_) { /* report below */ }
      }
      throw new Error('CSV 编码无效，请另存为 UTF-8 后重试。');
    }
  }

  function csvDelimiter(text) {
    const separators = [',', '\t', ';'];
    const scores = [0, 0, 0];
    let quoted = false, lines = 0;
    let counts = [0, 0, 0];
    // Count only separators outside quotes; a single-column title may precede the header.
    const end = Math.min(text.length, 65536);
    for (let i = 0; i <= end && lines < 12; i += 1) {
      const ch = text[i];
      if (ch === '"') quoted = !quoted;
      if (quoted) continue;
      if (ch === '\n' || ch === '\r' || i === end) {
        counts.forEach((count, j) => { scores[j] += count ? 1 + Math.min(count, 12) : 0; });
        counts = [0, 0, 0];
        lines += 1;
        if (ch === '\r' && text[i + 1] === '\n') i += 1;
      } else {
        const j = separators.indexOf(ch);
        if (j >= 0) counts[j] += 1;
      }
    }
    return separators[scores.indexOf(Math.max(...scores))];
  }

  function readCsv(bytes) {
    const text = decodeCsv(bytes);
    check(!/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/.test(text) && !/^\s*(?:<|%PDF-|version https:\/\/git-lfs\.github\.com\/spec\/)/i.test(text),
      '文件不是有效的 CSV 文本。');
    const sep = csvDelimiter(text);
    const rows = [], lines = [];
    let row = [], value = '', state = 0, count = 0, line = 1, rowLine = 1;
    const badQuote = 'CSV 引号不完整或格式有误。';
    function cell() {
      count += 1;
      check(row.length < LIMIT.columns && count <= LIMIT.cells, TOO_LARGE);
      row.push(value); value = ''; state = 0;
    }
    function record() {
      cell();
      check(rows.length < LIMIT.rows, TOO_LARGE);
      rows.push(row); lines.push(rowLine); row = [];
    }
    for (let i = 0; i < text.length; i += 1) {
      const ch = text[i];
      const newline = ch === '\r' || ch === '\n';
      const crlf = ch === '\r' && text[i + 1] === '\n';
      if (state === 1) { // quoted field
        if (ch === '"') {
          if (text[i + 1] === '"') { value += '"'; i += 1; }
          else state = 2;
        } else value += crlf ? '\r\n' : ch;
      } else if (newline) record();
      else if (ch === sep) cell();
      else if (ch === '"') { check(state === 0 && value === '', badQuote); state = 1; }
      else {
        check(state !== 2, badQuote);
        value += ch;
      }
      if (newline) {
        if (crlf) i += 1;
        line += 1;
        if (state !== 1) rowLine = line;
      }
      check(value.length <= LIMIT.text, TOO_LARGE);
    }
    check(state !== 1, badQuote);
    if (row.length || value || state === 2) record();
    check(rows.some(r => r.length > 1 && r.some(v => v.trim())), 'CSV 未包含可识别的表格列。');
    const sheet = { name: 'CSV', rows };
    sourceLines.set(sheet, lines);
    return { sheets: [sheet] };
  }

  const crcTable = Uint32Array.from({ length: 256 }, (_, i) => {
    for (let k = 0; k < 8; k += 1) i = (i >>> 1) ^ (i & 1 ? 0xedb88320 : 0);
    return i;
  });
  function crc32(bytes) {
    let crc = 0xffffffff;
    for (const byte of bytes) crc = (crc >>> 8) ^ crcTable[(crc ^ byte) & 255];
    return (crc ^ 0xffffffff) >>> 0;
  }

  function openZip(bytes) {
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    const u16 = i => view.getUint16(i, true);
    const u32 = i => view.getUint32(i, true);
    check(bytes.length >= 22 && u32(0) === 0x04034b50, NOT_XLSX);
    let eocd = bytes.length - 22;
    const first = Math.max(0, eocd - 65535);
    while (eocd >= first && !(u32(eocd) === 0x06054b50 && eocd + 22 + u16(eocd + 20) === bytes.length)) eocd -= 1;
    check(eocd >= first && !u16(eocd + 4) && !u16(eocd + 6), BAD_ZIP);
    const count = u16(eocd + 10), start = u32(eocd + 16);
    check(count > 0 && u16(eocd + 8) === count && start + u32(eocd + 12) === eocd, BAD_ZIP);
    check(count <= LIMIT.parts, TOO_LARGE);

    const entries = new Map(), folded = new Set(), spans = [];
    const names = new TextDecoder('utf-8', { fatal: true });
    let at = start, declared = 0;
    for (let i = 0; i < count; i += 1) {
      check(at + 46 <= eocd && u32(at) === 0x02014b50, BAD_ZIP);
      const flags = u16(at + 8), method = u16(at + 10), crc = u32(at + 16);
      const compressed = u32(at + 20), length = u32(at + 24), n = u16(at + 28), local = u32(at + 42);
      const next = at + 46 + n + u16(at + 30) + u16(at + 32);
      check(n > 0 && n <= 512 && next <= eocd && !u16(at + 34) && !(flags & ~0x080e) &&
        (method === 8 || (method === 0 && length === compressed && !(flags & 6))), BAD_ZIP);
      const rawName = bytes.subarray(at + 46, at + 46 + n);
      let name;
      try { name = names.decode(rawName); } catch (_) { throw new Error(BAD_ZIP); }
      const path = name.endsWith('/') ? name.slice(0, -1) : name;
      check(!/[\\:\x00-\x1f\x7f]/.test(name) && path.split('/').every(p => p && p !== '.' && p !== '..') &&
        !folded.has(name.toLowerCase()), BAD_ZIP);
      folded.add(name.toLowerCase());
      check(local + 30 <= start && u32(local) === 0x04034b50 && u16(local + 6) === flags &&
        u16(local + 8) === method && u16(local + 26) === n, BAD_ZIP);
      const data = local + 30 + n + u16(local + 28), end = data + compressed;
      check(end <= start && rawName.every((v, j) => bytes[local + 30 + j] === v), BAD_ZIP);
      if (!(flags & 8)) check(u32(local + 14) === crc && u32(local + 18) === compressed && u32(local + 22) === length, BAD_ZIP);
      declared += length;
      check(declared <= LIMIT.expanded, TOO_LARGE);
      spans.push([local, end]);
      entries.set(name, { method, crc, compressed, length, data });
      at = next;
    }
    spans.sort((a, b) => a[0] - b[0]);
    check(at === eocd && spans.every((span, i) => i === 0 || spans[i - 1][1] <= span[0]), BAD_ZIP);

    async function extract(name) {
      const entry = entries.get(name);
      check(entry, BAD_XML);
      const { method, crc, compressed, length, data } = entry;
      check(length <= LIMIT.xml && length <= Math.max(256 * 1024, compressed * 250), TOO_LARGE);
      const packed = bytes.subarray(data, data + compressed);
      let plain = packed;
      if (method === 8) {
        let inflater;
        try { inflater = new DecompressionStream('deflate-raw'); }
        catch (_) { throw new Error('当前浏览器无法解压 XLSX，请改用新版浏览器或将文件另存为 CSV。'); }
        // Limit each input chunk too: a dishonest size must not cause an unbounded
        // native expansion before the JavaScript length guard sees the first output.
        let cursor = 0;
        const stream = new ReadableStream({ pull(controller) {
          if (cursor === packed.length) controller.close();
          else {
            const end = Math.min(cursor + 4096, packed.length);
            controller.enqueue(packed.subarray(cursor, end));
            cursor = end;
          }
        } });
        const reader = stream.pipeThrough(inflater).getReader();
        plain = new Uint8Array(length);
        let written = 0;
        try {
          while (true) {
            const part = await reader.read();
            if (part.done) break;
            if (written + part.value.length > length) {
              await reader.cancel();
              throw new Error(BAD_ZIP);
            }
            plain.set(part.value, written);
            written += part.value.length;
          }
          check(written === length, BAD_ZIP);
        } catch (_) { throw new Error(BAD_ZIP); }
        finally { reader.releaseLock(); }
      }
      check(crc32(plain) === crc, BAD_ZIP);
      return plain;
    }
    return { entries, extract };
  }

  const CT = 'http://schemas.openxmlformats.org/package/2006/content-types';
  const PKG_REL = 'http://schemas.openxmlformats.org/package/2006/relationships';
  const MAIN = ['http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'http://purl.oclc.org/ooxml/spreadsheetml/main'];
  const DOC_REL = ['http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'http://purl.oclc.org/ooxml/officeDocument/relationships'];
  const XLSX_MAIN = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml';
  const XLSX_SHEET = 'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml';
  const XLSX_STRINGS = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml';

  function xmlRoot(bytes, tag, allowedNs) {
    let encoding = 'utf-8', xml;
    if (bytes[0] === 0xff && bytes[1] === 0xfe) encoding = 'utf-16le';
    if (bytes[0] === 0xfe && bytes[1] === 0xff) encoding = 'utf-16be';
    try { xml = new TextDecoder(encoding, { fatal: true }).decode(bytes); } catch (_) { throw new Error(BAD_XML); }
    check(!/<!\s*(?:DOCTYPE|ENTITY)\b/i.test(xml), BAD_XML);
    const dom = new DOMParser().parseFromString(xml, 'application/xml');
    const root = dom.documentElement;
    check(root && root.localName === tag && allowedNs.includes(root.namespaceURI) &&
      !dom.getElementsByTagNameNS('http://www.mozilla.org/newlayout/xml/parsererror.xml', 'parsererror').length, BAD_XML);
    return root;
  }

  function* children(node, tag) {
    if (!node) return;
    for (let el = node.firstElementChild; el; el = el.nextElementSibling) {
      if (el.namespaceURI === node.namespaceURI && el.localName === tag) yield el;
    }
  }
  function child(node, tag) { return children(node, tag).next().value; }
  function resolvePart(owner, target) {
    // OPC internal paths only; never dereference a URI or extract to the filesystem.
    check(target && !/[\\:%?#\x00-\x20\x7f]/.test(target), BAD_XML);
    const result = target.startsWith('/') ? [] : owner.split('/').slice(0, -1);
    for (const component of target.replace(/^\//, '').split('/')) {
      if (component === '..') { check(result.length, BAD_XML); result.pop(); }
      else if (component !== '.') { check(component, BAD_XML); result.push(component); }
    }
    check(result.length, BAD_XML);
    return result.join('/');
  }
  function relPath(owner) {
    const split = owner.lastIndexOf('/') + 1;
    return owner.slice(0, split) + '_rels/' + owner.slice(split) + '.rels';
  }
  function relationships(root) {
    const out = new Map();
    for (const el of children(root, 'Relationship')) {
      const id = el.getAttribute('Id');
      check(id && !out.has(id), BAD_XML);
      out.set(id, { type: el.getAttribute('Type'), mode: el.getAttribute('TargetMode'), target: el.getAttribute('Target') });
    }
    return out;
  }
  const isRel = (rel, kind) => rel && DOC_REL.some(ns => rel.type === ns + '/' + kind);
  const internal = rel => rel && (!rel.mode || rel.mode === 'Internal');
  function richText(node) {
    let text = child(node, 't')?.textContent || '';
    for (const run of children(node, 'r')) {
      text += child(run, 't')?.textContent || '';
      check(text.length <= LIMIT.text, TOO_LARGE);
    }
    check(text.length <= LIMIT.text, TOO_LARGE);
    // SpreadsheetML escape sequences are decoded once, never interpreted as markup.
    return text.replace(/_x([0-9a-f]{4})_/gi, (_, hex) => String.fromCharCode(parseInt(hex, 16)));
  }
  function sheetRows(root, strings, budget) {
    const rows = [], data = child(root, 'sheetData');
    check(data, BAD_XML);
    let rowNumber = 0;
    for (const row of children(data, 'row')) {
      const r = row.getAttribute('r');
      if (r !== null) check(/^[1-9]\d{0,6}$/.test(r), BAD_XML);
      const next = r === null ? rowNumber + 1 : Number(r);
      check(next > rowNumber, BAD_XML);
      check(next <= LIMIT.rows, TOO_LARGE);
      rowNumber = next;
      const items = [];
      rows[rowNumber - 1] = items;
      let column = 0;
      for (const c of children(row, 'c')) {
        budget.cells += 1;
        check(budget.cells <= LIMIT.cells, TOO_LARGE);
        const ref = c.getAttribute('r');
        let index = column + 1;
        if (ref !== null) {
          const parsed = /^([A-Z]{1,3})([1-9]\d{0,6})$/.exec(ref);
          check(parsed && Number(parsed[2]) === rowNumber, BAD_XML);
          index = 0;
          for (const ch of parsed[1]) index = index * 26 + ch.charCodeAt(0) - 64;
        }
        check(index > column, BAD_XML);
        check(index <= LIMIT.columns, TOO_LARGE);
        column = index;
        const type = c.getAttribute('t') || 'n';
        const formula = child(c, 'f');
        const stored = child(c, 'v')?.textContent || '';
        check(stored.length <= LIMIT.text, TOO_LARGE);
        if (type === 'n') {
          // A formula contributes only a numeric cache. It is never evaluated.
          const value = decimal(stored.trim());
          if (value !== null) items[column - 1] = value;
        } else if (!formula && type === 's') {
          check(/^\d{1,8}$/.test(stored) && +stored < strings.length, BAD_XML);
          items[column - 1] = strings[+stored];
        } else if (!formula && type === 'inlineStr') items[column - 1] = richText(child(c, 'is'));
        else if (!formula && (type === 'str' || type === 'd')) items[column - 1] = stored;
      }
    }
    return rows;
  }

  async function readXlsx(bytes) {
    const zip = openZip(bytes);
    const root = async (path, tag, ns) => xmlRoot(await zip.extract(path), tag, ns);
    check(zip.entries.has('[Content_Types].xml') && zip.entries.has('_rels/.rels') &&
      !Array.from(zip.entries.keys()).some(n => /(?:^|\/)vba(?:project|data)/i.test(n)), NOT_XLSX);
    const types = await root('[Content_Types].xml', 'Types', [CT]);
    const overrides = new Map();
    for (const tag of ['Default', 'Override']) {
      for (const node of children(types, tag)) {
        const type = node.getAttribute('ContentType');
        check(type && !/macroenabled|vba(project|data)/i.test(type), NOT_XLSX);
        if (tag === 'Override') {
          const name = node.getAttribute('PartName');
          check(name?.startsWith('/') && !overrides.has(name.slice(1)), BAD_XML);
          overrides.set(name.slice(1), type);
        }
      }
    }
    const packageRels = relationships(await root('_rels/.rels', 'Relationships', [PKG_REL]));
    const documents = Array.from(packageRels.values()).filter(rel => isRel(rel, 'officeDocument'));
    check(documents.length === 1 && internal(documents[0]), NOT_XLSX);
    const workbookPath = resolvePart('', documents[0].target);
    check(overrides.get(workbookPath) === XLSX_MAIN, NOT_XLSX);
    const workbook = await root(workbookPath, 'workbook', MAIN);
    const rels = relationships(await root(relPath(workbookPath), 'Relationships', [PKG_REL]));
    const shared = Array.from(rels.values()).filter(rel => isRel(rel, 'sharedStrings'));
    check(shared.length <= 1, BAD_XML);
    const strings = [];
    if (internal(shared[0])) {
      const path = resolvePart(workbookPath, shared[0].target);
      check(overrides.get(path) === XLSX_STRINGS, BAD_XML);
      const table = await root(path, 'sst', MAIN);
      for (const item of children(table, 'si')) {
        check(strings.length < LIMIT.cells, TOO_LARGE);
        strings.push(richText(item));
      }
    }
    const sheets = [], usedPaths = new Set(), budget = { cells: 0 };
    const listed = Array.from(children(child(workbook, 'sheets'), 'sheet'));
    check(listed.length <= LIMIT.sheets, TOO_LARGE);
    for (const sheet of listed) {
      if (sheet.getAttribute('state') === 'hidden' || sheet.getAttribute('state') === 'veryHidden') continue;
      const id = DOC_REL.map(ns => sheet.getAttributeNS(ns, 'id')).find(Boolean);
      const rel = rels.get(id);
      check(rel, BAD_XML);
      if (!isRel(rel, 'worksheet') || !internal(rel)) continue;
      const path = resolvePart(workbookPath, rel.target);
      check(overrides.get(path) === XLSX_SHEET && !usedPaths.has(path), BAD_XML);
      usedPaths.add(path);
      const name = sheet.getAttribute('name') || `工作表 ${sheets.length + 1}`;
      check(name.length <= LIMIT.text, TOO_LARGE);
      sheets.push({ name, rows: sheetRows(await root(path, 'worksheet', MAIN), strings, budget) });
    }
    check(sheets.length, 'XLSX 没有可读取的普通可见工作表。');
    return { sheets };
  }

  async function read(file) {
    const ext = /\.([^.]+)$/.exec(file?.name || '')?.[1].toLowerCase();
    check(ext === 'csv' || ext === 'xlsx', '仅支持 CSV 和 XLSX，不支持旧版 XLS、XLSM 或 PDF。');
    check(Number.isSafeInteger(file.size) && file.size > 0, '请选择非空表格文件。');
    check(file.size <= LIMIT.file, TOO_LARGE);
    const bytes = new Uint8Array(await file.arrayBuffer());
    check(bytes.length === file.size, '无法完整读取表格文件。');
    return ext === 'xlsx' ? readXlsx(bytes) : readCsv(bytes);
  }

  const FIELDS = {
    assets: ['总资产', '资产总计', '资产总额', '资产合计', 'total assets'],
    debt: ['总负债', '负债合计', '负债总计', '负债总额', 'total liabilities'],
    'current-assets': ['流动资产', '流动资产合计', '流动资产总计', '流动资产总额', 'total current assets', 'current assets'],
    'current-debt': ['流动负债', '流动负债合计', '流动负债总计', '流动负债总额', 'total current liabilities', 'current liabilities'],
    revenue: ['营业收入', '营业总收入', '主营业务收入', '销售收入', '营收', '营业额', 'revenue', 'total revenue', 'sales'],
    profit: ['净利润', '净利润合计', '净利润总额', 'net profit', 'net income'],
    cash: ['经营活动产生的现金流量净额', '经营活动现金流量净额', '经营活动现金流净额', '经营活动之现金流量净额',
      '经营现金流量净额', '经营现金流净额', '经营活动净现金流', '经营现金流', '经营活动现金流',
      'operating cash flow', 'net cash from operating activities', 'net cash provided by operating activities']
  };
  const IDS = Object.keys(FIELDS);
  const normalize = value => (typeof value === 'string' || typeof value === 'number' ? String(value) : '')
    .slice(0, LIMIT.text).normalize('NFKC').replace(/\s+/g, '').toLowerCase();
  const fieldFor = new Map(IDS.flatMap(id => FIELDS[id].map(label => [normalize(label), id])));
  const companyLabels = /^(?:公司名称|企业名称|公司|企业|单位名称|编制单位|company(?:name)?)$/;
  const periodLabels = /^(?:报告期|报表期|报告日期|报表日期|财报期间|报告期间|会计期间|年度|期间|截止日期|period|reportingperiod|year)$/;
  const unitLabels = /^(?:单位|金额单位|货币单位|币种和单位|unit)$/;
  const lineLabels = /^(?:行次|序号|行号|编号|附注|附注号|科目代码|百分比|比例|增减率|增长率|同比|环比|币种|备注|说明|row|no\.)$/;
  const metricLabels = /^(?:指标(?:名称)?|(?:财务)?项目(?:名称)?|科目(?:名称)?|财务指标|报表项目|item|indicator|metric)$/;
  const ambiguousLabels = /^(?:收入|总收入|利润|利润总额|归母净利润|归属于母公司股东的净利润|资产|负债|现金流|现金流量净额|现金及现金等价物净增加额|现金|现金净额)$/;
  const unitName = /^(?:人民币|rmb|cny)?(亿元|万元|元)(?:人民币)?$/;
  const declaredUnit = /^(?:金额单位|货币单位|币种和单位|单位)[:=](.+)$/;
  const otherUnit = /(?:千元|百万元|十亿元|美元|港元|港币|日元|欧元|英镑|usd|hkd|eur|jpy|%)/i;
  const terminalUnit = /(?:\(([^()]*)\)|[/:]([^/:]+))$/;
  const reportWord = /^(?:合并|母公司)(?:报表)?$/;
  const priorWord = /^(?:期初(?:余额|数)?|年初(?:余额|数)?|上(?:期|年)(?:金额|余额|数|发生额|同期)?)$/;
  const datePattern = /^(?:(?:19|20)\d{2})(?:(?:年(?:度|报|末|初|第?[一二三四1234]季度|\d{1,2}月(?:\d{1,2}日)?)?|[-/.]\d{1,2}(?:[-/.]\d{1,2})?(?:t\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:z|[+-]\d{2}:\d{2})?)?|q[1-4]|h[12]|中报|半年报|一季报|三季报|\d{4}))?$/;

  function unitOf(raw) {
    const s = normalize(raw);
    const declared = declaredUnit.exec(s);
    const token = (declared ? declared[1] : s).replace(/^\((.*)\)$/, '$1');
    return unitName.exec(token)?.[1] || (otherUnit.test(token) ? '?' : null);
  }
  function standaloneUnit(raw) {
    const s = normalize(raw).replace(/^\((.*)\)$/, '$1');
    return unitName.exec(s)?.[1] || (/^(?:人民币)?(?:千元|百万元|十亿元|美元|港元|港币|日元|欧元|英镑|usd|hkd|eur|jpy)$/.test(s) ? '?' : null);
  }
  function measureLabel(raw) {
    let label = normalize(raw).replace(/^(?:(?:[一二三四五六七八九十]+[、.、:]|\d+[、.:]|\([\d一二三四五六七八九十]+\))|(?:其中|加|减):)/, '');
    const tail = terminalUnit.exec(label);
    const unit = tail ? standaloneUnit(tail[1] ?? tail[2]) : null;
    if (unit) label = label.slice(0, tail.index);
    return { label, unit, id: fieldFor.get(label) };
  }

  function decimal(raw) {
    if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(raw)) return null;
    const value = Number(raw);
    if (!Number.isFinite(value) || Math.abs(value) > Number.MAX_SAFE_INTEGER ||
      (value === 0 && /[1-9]/.test(raw.split(/e/i)[0]))) return null;
    return value === 0 ? 0 : value;
  }
  function amount(raw) {
    if (typeof raw === 'number') return decimal(String(raw)) === null ? null : { value: raw, unit: null };
    if (typeof raw !== 'string' || raw.length > LIMIT.text) return null;
    let s = raw.normalize('NFKC').trim().replace(/−/g, '-');
    const tail = /(?:人民币)?(亿元|万元|元)(?:人民币)?$/.exec(s);
    if (tail) s = s.slice(0, tail.index).trim();
    const negative = s.startsWith('(') && s.endsWith(')');
    if (negative) s = s.slice(1, -1).trim();
    s = s.replace(/^(人民币|￥|¥)\s*/, '');
    if (negative && /^[+-]/.test(s)) return null;
    if (s.includes(',')) {
      if (!/^[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?$/.test(s)) return null;
      s = s.replace(/,/g, '');
    } else if (/\s/.test(s)) {
      if (!/^[+-]?\d{1,3}(?: \d{3})+(?:\.\d+)?$/.test(s)) return null;
      s = s.replace(/ /g, '');
    }
    const value = decimal((negative ? '-' : '') + s);
    return value === null ? null : { value, unit: tail?.[1] || null };
  }
  function metaText(value, period) {
    if (typeof value === 'number') return period && datePattern.test(String(value)) ? String(value) : '';
    if (typeof value !== 'string') return '';
    const s = value.replace(/[\x00-\x1f\x7f]/g, ' ').trim().slice(0, 120);
    return /^[=+@-]/.test(s) ? '' : s;
  }
  function metaRole(label) {
    if (companyLabels.test(label)) return 'company';
    if (periodLabels.test(label)) return 'period';
    return null;
  }
  function headingRank(label) {
    if (/^(?:本期|当期|本年|本年度|本报告期|期末|年末)(?:金额|余额|数|发生额|累计(?:金额|数)?)?$/.test(label)) return 3;
    if (datePattern.test(label) || reportWord.test(label)) return 2;
    if (priorWord.test(label) || /^(?:金额|数值|数据|金额值|value|amount)$/.test(label)) return 1;
    return 0;
  }

  function analyze(sheet) {
    const values = {}, sources = {}, meta = {}, warnings = [], usedUnits = [];
    const rows = (Array.isArray(sheet?.rows) ? sheet.rows : []).slice(0, LIMIT.rows);
    const cells = rows.map(row => Array.isArray(row) ? row.slice(0, LIMIT.columns).map(measureLabel) : []);
    let invalid = false, ambiguous = false;
    const cell = (r, c) => rows[r]?.[c];
    function location(r, c) {
      let letters = '';
      for (let n = c + 1; n > 0; n = Math.floor((n - 1) / 26)) letters = String.fromCharCode(65 + (n - 1) % 26) + letters;
      return letters + (sourceLines.get(sheet)?.[r] ?? r + 1);
    }
    function setMeta(context, role, raw) {
      const value = metaText(raw, role === 'period');
      if (value && !context[role]) context[role] = value;
    }
    function splitHeading(r, c) {
      const raw = cell(r, c);
      const inline = typeof raw === 'string' && /^([^:：]+)[:：]\s*(.+)$/.exec(raw.trim());
      return inline ? [normalize(inline[1]), inline[2]] : [cells[r][c]?.label, cell(r, c + 1)];
    }
    function contextAt(r, context) {
      cells[r]?.forEach((_, c) => {
        const [label, raw] = splitHeading(r, c);
        const role = metaRole(label);
        if (role) setMeta(context, role, raw);
        if (unitLabels.test(label)) {
          const u = unitOf(raw);
          if (u) context.units.push(u);
        }
      });
    }
    function write(id, r, c, result, local, fallback) {
      if (!result) { if (normalize(cell(r, c))) invalid = true; return; }
      values[id] = result.value;
      sources[id] = location(r, c);
      const explicit = [result.unit, ...local].filter(Boolean);
      usedUnits.push(...(explicit.length ? explicit : fallback.length ? fallback : [null]));
    }

    // A horizontal record is always taken from one row and from the first header group only.
    const horizontal = [];
    cells.forEach((row, at) => {
      const firstMetric = row.findIndex(info => info?.id);
      if (firstMetric < 0) return;
      const metrics = new Map(), extra = {}, groups = [];
      const above = cells[at - 1] || [];
      const groupLabel = label => datePattern.test(label) || reportWord.test(label);
      if (!above.some((info, c) => info.id || (!groupLabel(info.label) && amount(cell(at - 1, c))))) {
        above.forEach(({ label }, c) => { if (groupLabel(label)) groups.push({ label, c }); });
      }
      const group = groups.length > 1 ? groups.filter(g => g.c <= firstMetric).pop() : null;
      const nextGroup = group ? groups.find(g => g.c > firstMetric)?.c : undefined;
      let repeated = false;
      row.forEach((info, c) => {
        if (repeated) return;
        if (c >= (nextGroup ?? Infinity)) { if (info.id) repeated = true; return; }
        const role = metaRole(info.label);
        if (role) {
          if (extra[role] != null && metrics.size) { repeated = true; return; }
          if (extra[role] == null) extra[role] = c;
        }
        if (unitLabels.test(info.label) && extra.unit == null) extra.unit = c;
        if (info.id) {
          if (metrics.has(info.id)) repeated = true;
          else metrics.set(info.id, { c, unit: info.unit });
        }
      });
      if (metrics.size >= 2 || (metrics.size && (group || repeated || extra.period != null || extra.company != null))) {
        const groupPeriod = group && datePattern.test(group.label) ? metaText(cell(at - 1, group.c), true) : '';
        horizontal.push({ at, metrics, extra, repeated, groupPeriod });
      }
    });
    let selected = null, horizontalCount = 0;
    horizontal.forEach((header, i) => {
      const metricCols = [...header.metrics.values()];
      for (let r = header.at + 1; r < (horizontal[i + 1]?.at ?? rows.length); r += 1) {
        if (metricCols.some(({ c }) => cells[r]?.[c]?.id) || !metricCols.some(({ c }) => amount(cell(r, c)))) continue;
        horizontalCount += 1;
        if (!selected) selected = { header, r, i };
      }
    });
    if (selected) {
      const { header, r, i } = selected;
      const { metrics, extra, repeated, groupPeriod } = header;
      const context = { units: [] };
      for (let j = i ? horizontal[i - 1].at + 1 : 0; j < header.at; j += 1) contextAt(j, context);
      Object.assign(meta, { company: context.company, period: groupPeriod || context.period });
      for (const role of ['company', 'period']) {
        if (extra[role] != null) meta[role] = metaText(cell(r, extra[role]), role === 'period') || (role === 'period' ? groupPeriod : '');
      }
      const unitCell = unitOf(cell(r, extra.unit));
      metrics.forEach(({ c, unit }, id) => write(id, r, c, amount(cell(r, c)), [unitCell, unit], context.units));
      ambiguous = cells[header.at].some(info => ambiguousLabels.test(info.label));
      if (repeated) warnings.push('表头包含并列分组或重复指标，仅使用第一组列，请核对报告期和报表口径。');
      if (horizontalCount > 1 || horizontal.length > 1) warnings.push('检测到多行数据或多个报告期，仅使用第一条可用记录，未合并其他行。');
    } else {
      // For vertical data, a header, repeated metric, or new entity/period starts a new block.
      // Within the chosen block all values must come from one physical amount column.
      const labelScores = Array(LIMIT.columns).fill(0);
      cells.forEach(row => row.forEach(({ id, label }, c) => {
        if (id) labelScores[c] += 2;
        if (metricLabels.test(label)) labelScores[c] += 1;
      }));
      const labelCol = labelScores.indexOf(Math.max(...labelScores));
      const blocks = [];
      let block, context;
      function start(header = -1, previous = null) {
        block = { header, metrics: new Map(), context: { ...(previous || {}), units: [...(previous?.units || [])] }, ambiguous: false };
        context = block.context;
        blocks.push(block);
      }
      start();
      cells.forEach((row, r) => {
        const info = row[labelCol];
        if (!info) return;
        const [label] = splitHeading(r, labelCol);
        const periodTitle = datePattern.test(info.label) && !row.slice(labelCol + 1).some((_, i) => normalize(cell(r, labelCol + 1 + i)));
        if (metricLabels.test(info.label)) start(r, block.metrics.size ? null : context);
        else if ((metaRole(label) || periodTitle) && block.metrics.size) start(-1);
        else if (info.id && block.metrics.has(info.id)) start(block.header);
        if (periodTitle) setMeta(context, 'period', cell(r, labelCol));
        if (info.id) block.metrics.set(info.id, { r, unit: info.unit });
        if (ambiguousLabels.test(info.label)) block.ambiguous = true;
        contextAt(r, context);
      });
      const usable = [];
      for (const b of blocks) {
        if (!b.metrics.size) continue;
        const headings = cells[b.header] || [];
        const unitCol = headings.findIndex(({ label }) => unitLabels.test(label));
        const maxCol = Math.max(headings.length, ...Array.from(b.metrics.values(), ({ r }) => cells[r].length));
        const columns = [];
        for (let c = labelCol + 1; c < maxCol; c += 1) {
          const label = headings[c]?.label || '';
          if (lineLabels.test(label) || unitLabels.test(label) || metaRole(label)) continue;
          if ([...b.metrics.values()].some(({ r }) => amount(cell(r, c)))) columns.push({ c, rank: headingRank(label) });
        }
        if (!columns.length) continue;
        columns.sort((a, b) => b.rank - a.rank || a.c - b.c);
        usable.push({ b, columns, unitCol });
      }
      if (usable.length) {
        const { b, columns, unitCol } = usable[0];
        const c = columns[0].c;
        const heading = cells[b.header]?.[c];
        Object.assign(meta, { company: b.context.company, period: b.context.period });
        if (heading && datePattern.test(heading.label)) meta.period = metaText(cell(b.header, c), true);
        if (heading && priorWord.test(heading.label)) {
          delete meta.period;
          warnings.push('所选金额列标为上期或期初，未沿用表头报告期，请核对实际期间。');
        }
        b.metrics.forEach(({ r, unit }, id) => {
          const rowUnits = unitCol >= 0 ? [unitOf(cell(r, unitCol))]
            : columns.length === 1 ? cells[r].map((_, j) => j > labelCol ? standaloneUnit(cell(r, j)) : null) : [];
          write(id, r, c, amount(cell(r, c)), [unit, heading?.unit, ...rowUnits], b.context.units);
        });
        ambiguous = b.ambiguous;
        if (usable.length > 1) warnings.push('检测到多个报表区块、重复指标或多个报告期，仅使用第一个可用区块，未合并其他区块。');
        if (columns.length > 1) warnings.push(columns[0].rank > columns[1].rank
          ? '检测到多列金额，仅使用表头优先的一列，未合并其他报告期或报表口径。'
          : '检测到多列金额，报告期或报表口径不唯一，仅使用自左起第一列可用金额，未合并其他列。');
      } else ambiguous = blocks.some(b => b.ambiguous);
    }
    const units = new Set(usedUnits.filter(Boolean));
    const unitHint = units.size === 1 && !units.has('?') ? units.values().next().value : null;
    if (units.size > 1 || units.has('?')) warnings.push('金额单位不一致或不在支持范围内，保留原数值且不推断统一单位，请核对原表。');
    else if (unitHint && usedUnits.includes(null)) warnings.push('部分金额没有标注单位，请核对全表是否使用同一单位。');
    if (ambiguous) warnings.push('存在口径不明确的指标名称，未将这些指标自动映射。');
    if (invalid) warnings.push('部分已识别字段不是可用的财务数值，已跳过。');
    const missing = IDS.filter(id => !Object.prototype.hasOwnProperty.call(values, id));
    if (missing.length === IDS.length) warnings.push('没有识别到可用的财务数据，请检查财务指标名称和金额列。');
    for (const role of ['company', 'period']) if (!meta[role]) delete meta[role];
    return { values, sources, missing, warnings, meta, unitHint };
  }

  window.CreditTableImport = Object.freeze({ read, analyze });
}());
