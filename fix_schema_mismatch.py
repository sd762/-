import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Line 492
old_1 = """body: JSON.stringify(localRecords.map(r => ({
                                audit_date: r.date,
                                template_id: r.templateId,
                                audit_name: r.auditName,
                                unit_category: r.unitCategory,
                                unit: String(r.unit || '').trim(),
                                target: r.target,
                                job_title: r.jobTitle,
                                auditor: r.auditor,
                                score: r.score,
                                score2: r.score2,
                                notes: r.notes,
                                is_dual: !!r.isDual,
                                technique: r.technique,
                                checklist: r.checklist
                            })))"""

new_1 = """body: JSON.stringify(localRecords.map(r => ({
                                audit_content: {
                                    date: r.date,
                                    templateId: r.templateId,
                                    auditName: r.auditName,
                                    unitCategory: r.unitCategory,
                                    unit: String(r.unit || '').trim(),
                                    target: r.target,
                                    jobTitle: r.jobTitle,
                                    auditor: r.auditor,
                                    score: r.score,
                                    score2: r.score2,
                                    notes: r.notes,
                                    isDual: !!r.isDual,
                                    technique: r.technique,
                                    checklist: r.checklist
                                }
                            })))"""

content = content.replace(old_1, new_1)

# 2. Line 1473
old_2 = "let url = `${supabaseUrl}/rest/v1/audit_records?select=*&order=audit_date.desc`;"
new_2 = "let url = `${supabaseUrl}/rest/v1/audit_records?select=*&order=created_at.desc`;"
content = content.replace(old_2, new_2)

# 3. Line 1481
old_3 = """setRecords(recs.map(r => ({
                            id: r.id, date: r.audit_date, templateId: r.template_id, auditName: r.audit_name,
                            unitCategory: r.unit_category, unit: String(r.unit || '').trim(), target: r.target, jobTitle: r.job_title,
                            auditor: r.auditor, score: r.score, score2: r.score2, notes: r.notes,
                            isDual: r.is_dual, technique: r.technique, checklist: r.checklist
                        })));"""

new_3 = """setRecords(recs.map(r => {
                            const data = typeof r.audit_content === 'string' ? JSON.parse(r.audit_content) : (r.audit_content || {});
                            return {
                                id: r.id, date: data.date || (r.created_at || '').split('T')[0], templateId: data.templateId, auditName: data.auditName,
                                unitCategory: data.unitCategory, unit: String(data.unit || '').trim(), target: data.target, jobTitle: data.jobTitle,
                                auditor: data.auditor, score: data.score, score2: data.score2, notes: data.notes,
                                isDual: data.isDual, technique: data.technique, checklist: data.checklist || []
                            };
                        }));"""
content = content.replace(old_3, new_3)

# 4. Line 1548
old_4 = """body: JSON.stringify({
                                        audit_date: r.date,
                                        template_id: r.templateId || null,
                                        audit_name: r.auditName,
                                        unit_category: r.unitCategory || '',
                                        unit: String(r.unit || '').trim(),
                                        target: r.target || '',
                                        job_title: r.jobTitle || '',
                                        auditor: r.auditor || '',
                                        score: r.score,
                                        score2: r.score2 || null,
                                        notes: r.notes || '',
                                        is_dual: !!r.isDual,
                                        technique: r.technique || '',
                                        checklist: r.checklist || [],
                                        user_id: session.user.id
                                    })"""

new_4 = """body: JSON.stringify({
                                        audit_content: {
                                            date: r.date,
                                            templateId: r.templateId || null,
                                            auditName: r.auditName,
                                            unitCategory: r.unitCategory || '',
                                            unit: String(r.unit || '').trim(),
                                            target: r.target || '',
                                            jobTitle: r.jobTitle || '',
                                            auditor: r.auditor || '',
                                            score: r.score,
                                            score2: r.score2 || null,
                                            notes: r.notes || '',
                                            isDual: !!r.isDual,
                                            technique: r.technique || '',
                                            checklist: r.checklist || []
                                        },
                                        user_id: session.user.id
                                    })"""
content = content.replace(old_4, new_4)

# 5. Line 2561
old_5 = """body: JSON.stringify({
                                audit_date: newRec.date,
                                template_id: currentTemplateId,
                                audit_name: newRec.auditName,
                                unit_category: newRec.unitCategory,
                                unit: String(newRec.unit || '').trim(),
                                target: newRec.target,
                                job_title: newRec.jobTitle,
                                auditor: newRec.auditor,
                                score: newRec.score,
                                score2: newRec.score2,
                                notes: newRec.notes,
                                is_dual: !!newRec.isDual,
                                technique: newRec.technique,
                                checklist: newRec.checklist || [],
                                user_id: session.user.id
                            })"""

new_5 = """body: JSON.stringify({
                                audit_content: {
                                    date: newRec.date,
                                    templateId: currentTemplateId,
                                    auditName: newRec.auditName,
                                    unitCategory: newRec.unitCategory,
                                    unit: String(newRec.unit || '').trim(),
                                    target: newRec.target,
                                    jobTitle: newRec.jobTitle,
                                    auditor: newRec.auditor,
                                    score: newRec.score,
                                    score2: newRec.score2,
                                    notes: newRec.notes,
                                    isDual: !!newRec.isDual,
                                    technique: newRec.technique,
                                    checklist: newRec.checklist || []
                                },
                                user_id: session.user.id
                            })"""
content = content.replace(old_5, new_5)

# 6. Line 2713
old_6 = """body: JSON.stringify(allImported.map(r => ({
                                    id: r.id,
                                    audit_date: r.date,
                                    audit_name: r.auditName,
                                    unit_category: r.unitCategory || '',
                                    unit: String(r.unit || '').trim(),
                                    target: r.target || '',
                                    job_title: r.jobTitle || '',
                                    auditor: r.auditor || '',
                                    score: r.score,
                                    score2: r.score2 || null,
                                    notes: r.notes || '',
                                    is_dual: !!r.isDual,
                                    technique: r.technique || '',
                                    checklist: r.checklist || [],
                                    user_id: session.user.id
                                })))"""

new_6 = """body: JSON.stringify(allImported.map(r => ({
                                    id: r.id,
                                    audit_content: {
                                        date: r.date,
                                        auditName: r.auditName,
                                        unitCategory: r.unitCategory || '',
                                        unit: String(r.unit || '').trim(),
                                        target: r.target || '',
                                        jobTitle: r.jobTitle || '',
                                        auditor: r.auditor || '',
                                        score: r.score,
                                        score2: r.score2 || null,
                                        notes: r.notes || '',
                                        isDual: !!r.isDual,
                                        technique: r.technique || '',
                                        checklist: r.checklist || [],
                                        templateId: r.templateId || null
                                    },
                                    user_id: session.user.id
                                })))"""
content = content.replace(old_6, new_6)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Done fixing schema mismatch.")
