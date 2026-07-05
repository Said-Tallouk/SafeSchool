import { jsPDF } from 'jspdf'

const TYPES_LABELS = {
  'التحرش الجسدي':           'Harcèlement physique',
  'التحرش اللفظي':           'Harcèlement verbal',
  'التحرش الإلكتروني':       'Cyberharcèlement',
  'العنف اللفظي أو التهديد': 'Violence verbale / Menace',
  'الإقصاء الاجتماعي':       'Exclusion sociale',
  'التمييز':                 'Discrimination',
  'التمييز العرقي':           'Discrimination raciale',
  'التمييز الجنسي':           'Discrimination sexiste',
  'التمييز الديني':           'Discrimination religieuse',
  'التحرش الجنسي':           'Harcèlement sexuel',
  'أخرى':                    'Autre',
}

const STATUS_LABELS = {
  'جديد':         'Nouveau',
  'قيد المعالجة': 'En cours',
  'موعد محدد':    'RDV fixé',
  'تم الحل':      'Résolu',
}

const APPT_LABELS = {
  'مقترح': 'Proposé',
  'مقبول': 'Accepté',
  'مرفوض': 'Refusé',
}

/**
 * Generate a professional PDF for a dossier
 * @param {Object} r - report object from the store
 */
export function generateDossierPDF(r) {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const W = 210
  const margin = 18
  const contentW = W - margin * 2
  let y = 0

  /* ── Helpers ── */
  function ln(n = 5) { y += n }

  function text(str, x, size = 10, style = 'normal', color = [30, 41, 59]) {
    doc.setFontSize(size)
    doc.setFont('helvetica', style)
    doc.setTextColor(...color)
    doc.text(str, x, y)
  }

  function multiline(str, x, maxW, size = 10) {
    doc.setFontSize(size)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(51, 65, 85)
    const lines = doc.splitTextToSize(str || '—', maxW)
    doc.text(lines, x, y)
    return lines.length
  }

  function rect(x, yy, w, h, fillColor) {
    doc.setFillColor(...fillColor)
    doc.roundedRect(x, yy, w, h, 2, 2, 'F')
  }

  function sectionHeader(label) {
    ln(4)
    rect(margin, y - 4, contentW, 7, [241, 245, 249])
    doc.setFontSize(8)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(100, 116, 139)
    doc.text(label.toUpperCase(), margin + 3, y)
    ln(6)
  }

  function hrLine() {
    doc.setDrawColor(226, 232, 240)
    doc.setLineWidth(0.3)
    doc.line(margin, y, W - margin, y)
    ln(4)
  }

  /* ── Header band ── */
  rect(0, 0, W, 34, [15, 148, 136])
  y = 12
  doc.setFontSize(18)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(255, 255, 255)
  doc.text('SafeSchool', margin, y)
  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(204, 251, 241)
  doc.text('Rapport de dossier confidentiel', margin, y + 7)

  // Status badge top right
  const statusLabel = STATUS_LABELS[r.status] || r.status
  doc.setFontSize(9)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(255, 255, 255)
  doc.text(`Statut : ${statusLabel}`, W - margin, y, { align: 'right' })
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(204, 251, 241)
  doc.text(`Dossier #${r.id}`, W - margin, y + 7, { align: 'right' })

  y = 40

  /* ── Meta info row ── */
  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(100, 116, 139)
  const dateStr = new Date(r.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'long', year: 'numeric'
  })
  doc.text(`Date de signalement : ${dateStr}`, margin, y)
  doc.text(
    `Type : ${TYPES_LABELS[r.report_type] || r.report_type}`,
    W - margin, y, { align: 'right' }
  )
  ln(5)
  hrLine()

  /* ── Informations sur l'élève ── */
  sectionHeader('Informations sur l\'élève')

  const col1 = margin + 3
  const col2 = margin + contentW / 2

  text('Nom complet', col1, 9, 'bold', [100, 116, 139])
  ln(5)
  text(r.student_name || '—', col1, 11, 'bold', [30, 41, 59])

  y -= 10
  text('Classe', col2, 9, 'bold', [100, 116, 139])
  ln(5)
  text(r.student_classe || '—', col2, 11, 'normal', [30, 41, 59])
  ln(6)

  if (r.student_telephone || r.student_email) {
    text('Téléphone', col1, 9, 'bold', [100, 116, 139])
    ln(5)
    text(r.student_telephone || '—', col1, 10, 'normal', [30, 41, 59])

    y -= 10
    text('E-mail', col2, 9, 'bold', [100, 116, 139])
    ln(5)
    text(r.student_email || '—', col2, 10, 'normal', [30, 41, 59])
    ln(4)
  }

  hrLine()

  /* ── Description de l'incident ── */
  sectionHeader('Description de l\'incident')

  if (r.location) {
    text(`📍 Lieu : ${r.location}`, col1, 9, 'italic', [100, 116, 139])
    ln(6)
  }
  if (r.perpetrator) {
    text(`Auteur présumé : ${r.perpetrator}`, col1, 9, 'italic', [100, 116, 139])
    ln(6)
  }

  rect(margin, y - 2, contentW, 4 + multiline(r.description, col1, contentW - 6, 10) * 5, [248, 250, 252])
  const descLines = multiline(r.description, col1, contentW - 6, 10)
  ln(descLines * 5 + 4)
  hrLine()

  /* ── Rendez-vous ── */
  if (r.appointment) {
    sectionHeader('Rendez-vous')

    const apptDate = new Date(r.appointment.date).toLocaleDateString('fr-FR', {
      weekday: 'long', day: '2-digit', month: 'long', year: 'numeric'
    })
    text(`Date : ${apptDate}`, col1, 10, 'normal', [30, 41, 59])
    ln(5)
    text(`Heure : ${r.appointment.time.slice(0, 5)}`, col1, 10, 'normal', [30, 41, 59])
    ln(5)
    text(`Statut RDV : ${APPT_LABELS[r.appointment.status] || r.appointment.status}`, col1, 10, 'normal', [30, 41, 59])
    ln(5)
    if (r.appointment.note) {
      text('Note :', col1, 9, 'bold', [100, 116, 139])
      ln(5)
      multiline(r.appointment.note, col1, contentW - 6)
      ln(8)
    }
    hrLine()
  }

  /* ── Compte-rendu de séance ── */
  if (r.session_report) {
    sectionHeader('Compte-rendu de séance')

    text('Rapport / Observations', col1, 9, 'bold', [100, 116, 139])
    ln(5)
    const summaryLines = multiline(r.session_report.summary, col1, contentW - 6)
    ln(summaryLines * 5 + 4)

    if (r.session_report.solutions) {
      text('Solutions proposées', col1, 9, 'bold', [100, 116, 139])
      ln(5)
      const solLines = multiline(r.session_report.solutions, col1, contentW - 6)
      ln(solLines * 5 + 4)
    }

    if (r.session_report.notes) {
      text('Notes supplémentaires', col1, 9, 'bold', [100, 116, 139])
      ln(5)
      const notesLines = multiline(r.session_report.notes, col1, contentW - 6)
      ln(notesLines * 5 + 4)
    }
    hrLine()
  }

  /* ── Footer ── */
  const pageH = doc.internal.pageSize.height
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(148, 163, 184)
  doc.text(
    `Document généré le ${new Date().toLocaleDateString('fr-FR')} — SafeSchool — Confidentiel`,
    W / 2, pageH - 10,
    { align: 'center' }
  )
  doc.setDrawColor(226, 232, 240)
  doc.setLineWidth(0.3)
  doc.line(margin, pageH - 14, W - margin, pageH - 14)

  /* ── Save ── */
  const filename = `SafeSchool_Dossier_${r.id}_${r.student_name?.replace(/\s+/g, '_') || 'Eleve'}.pdf`
  doc.save(filename)
}
