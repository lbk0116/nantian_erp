# -*- coding: utf-8 -*-

import openerp
from docxtpl import DocxTemplate,InlineImage
from docx.shared import Mm, Inches, Pt

import re
from cStringIO import StringIO

import urllib2
import json
import base64
import zipfile,os
import sys
from datetime import datetime

import requests

from openerp import http
from openerp.tools import ustr
from openerp.http import request



def content_disposition(filename):
    filename = ustr(filename)
    escaped = urllib2.quote(filename.encode('utf8'))
    browser = request.httprequest.user_agent.browser
    version = int((request.httprequest.user_agent.version or '0').split('.')[0])
    if browser == 'msie' and version < 9:
        return "attachment; filename=%s" % escaped
    elif browser == 'safari' and version < 537:
        return u"attachment; filename=%s" % filename.encode('ascii', 'replace')
    else:
        return "attachment; filename*=UTF-8''%s" % escaped


# class exchange_data(http.Controller):
#     @http.route('/get_ip/', type='http', auth='public', methods=['POST'])
#     def get_ip(self, **post):
#         if post['pwd'] == '123':
#             ip = http.request.httprequest.remote_addr
#
#         boos_ip = http.request.env['server_desk.case'].search([('special', '=', 'boss')],limit=1)
#         boos_ip.ip = ip
#         return "ok"

class Binary(http.Controller):
    @http.route('/web/binary/html_page', type='http', auth="public")
    #@serialize_exception
    def html_page(self, model, field, id=None, filename_field=None, **kw):
        """ Download link for files stored as binary fields.

        If the ``id`` parameter is omitted, fetches the default value for the
        binary field (via ``default_get``), otherwise fetches the field for
        that precise record.

        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename_field: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context
        fields = [field]
        if filename_field:
            fields.append(filename_field)
        if id:
            res = Model.read(cr, uid, [int(id)], fields, context)[0]
        else:
            res = Model.default_get(cr, uid, fields, context)
        filecontent = base64.b64decode(res.get(field) or '')
        if not filecontent:
            return request.not_found()
        else:
            filename = '%s_%s' % (model.replace('.', '_'), id)
            if filename_field:
                filename = res.get(filename_field, '') or filename
            return request.make_response(filecontent,
                [('Content-Type', 'text/html')])

    @http.route('/nantian_erp/export_resume', type='http', auth="public")
    def export_resume(self,ids):
        # 定义压缩文件流
        zip_stream = StringIO()
        resume_zip = zipfile.ZipFile(zip_stream,'w')
        # 将参数转为列表
        id_list = json.loads(ids)
        # 获取要到处简历的员工
        Model = request.session.model('hr.employee')
        employees = Model.search_read([('id','in',id_list)])
        job=''

        for i,employee in enumerate(employees):

            # 获取模板
            path = os.path.abspath(os.path.dirname(sys.argv[0]))
            tpl = DocxTemplate(path.replace('\\','/')+'/myaddons/nantian_erp/resume_template.docx')
            # 简历写入的文件流
            fp = StringIO()
            experiences_list = []
            certifications_dict=[]
            if employee['job_id']:
                job = employee['job_id'][1]
            if employee['work_experience_ids']:
                Model = request.session.model('nantian_erp.work_experience')
                experiences = Model.search_read([('id','in',employee['work_experience_ids'])])
                for exper in experiences:
                    exper_dict = {'date':exper['date'] or '','name':exper['name'] or '','job':exper['job'] or '','description':exper['description'] or ''}
                    experiences_list.append(exper_dict)

            if employee['certificate_ids']:
                count = 0
                Model = request.session.model('nantian_erp.certificate')
                certificates = Model.search_read([('id','in',employee['certificate_ids'])])
                for cer in certificates:
                    count = count + 1
                    image = ''
                    name = ''
                    if cer['image']:
                        # 将base64 转为图片
                        f = StringIO(base64.b64decode(str(cer['image'])))
                        print "查看图片名称%d"%count
                        try:
                            image = InlineImage(tpl,f)
                        except Exception:
                            pass
                        #image = InlineImage(tpl,f,height=Mm(30))
                        f.close()
                    if cer['name']:
                        name = cer['name'].replace('&','&amp;')
                    certificate = {'name':name or '','image': image or '',}

                    certifications_dict.append(certificate)
            gender = ''
            if employee['gender'] == 'male':
                gender = u'男'
            elif employee['gender'] == 'female':
                gender = u'女'
            # 模板所需数据
            resume_dict = {'name':employee['name'] or '',
                           'gender':gender or '',
                           'birthday':employee['birthday']or '',
                           'education':employee['education']or '',
                           'graduction':employee['graduation']or '',
                           'major':employee['major']or '',
                           'job':job or '',
                           'work_time':employee['work_time']or '',
                           'specialty':employee['specialty']or '',
                           'work_experiences':experiences_list or [],
                           'certifications':certifications_dict or [],
                           }
            # encode_json = json.dumps(resume_dict)
            # rep_resume_dict = encode_json.replace('&','&amp;')
            # resume_dict = json.loads(rep_resume_dict)
            # print resume_dict
            tpl.render(resume_dict)
            tpl.save(fp)
            fp.seek(0)
            resume_zip.writestr(employee['name']+u'简历'+'.docx',fp.getvalue())
            fp.close()
        resume_zip.close()
        zip_stream.seek(0)
        # 返回压缩文件
        return request.make_response(zip_stream.getvalue() ,
            headers=[('Content-Disposition',content_disposition(u'简历'+'.zip')),
                     ('Content-Type', 'application/zip')],
            )


class SynchronousResume(http.Controller):

    def search_model(self,model,domain):
        search_model = http.request.env[model]
        records = search_model.sudo().search(domain)
        return records

    @http.route('/nantian_erp/SynchronousResume/get_data/', type='http', auth='public')
    def get_data(self,):
        r = requests.get('http://123.56.147.94/talents/get_all_position_and_examine')
        positions = r.json()
        #print positions
        cate_model = request.session.model('nantian_erp.categroy')
        categroy = cate_model.create({'name':'原系统'})
        for position in positions:
            job_model = request.session.model('nantian_erp.job')
            job = job_model.create({'name':position['PositionName'],'categroy_id':categroy})
            # users = http.request.env['res.users'].sudo().search([('name','=',position['UserID'])])
            users=self.search_model('res.users',[('name','=',position['UserID'])])
            if users:
                user = users[0].id
            else:
                user = None
            departs = self.search_model('hr.department',[('name','=',position['Depart'])])
            if departs:
                depart =departs[0].id

            else:
                depart = None
            working_teams = self.search_model('nantian_erp.working_team',[('name','=',position['ProjectName'])])
            if working_teams:
                working_team = working_teams[0].id
            else:
                working_team=None
            examine_users=self.search_model('res.users',[('name','=',position['Approver'])])
            if examine_users:
                exam_user = examine_users[0].id
            else:
                exam_user = None
            if position['Filing'] == 1:
                state='archived'
            elif position['Filing'] == 0:
                state='released'
            else:
                pass
            recr_dict={'user_id':user,'department_id':depart,'working_team_id':working_team,'position_categroy_1':categroy,'job_id':job,'duties':position['WorkContent'],'requirements':position['CandidateRequirement'],'salary':position["Salary"],'current_employee_num':position["ExistingPersonNum"],'need_people_num':position['NeedPersonNum'],'reason':str(position["RecruitReason"])
 ,'channel':str(position['RecruitWay']),'cycle':position['RecruitTime'],'state':state,'examine_user':exam_user,'hired_num':position['recruitednum'],'work_place':position['Workplace']}
            rec_model = request.session.model('nantian_erp.recruitment')
            recruit = rec_model.create(recr_dict)
            examine_model = request.session.model('nantian_erp.job_examine')
            examines = position['examine']
            for examine in examines:
                exam_users = self.search_model('res.users',[('name','=',examine['UserID'])])
                if exam_users:
                    ex_user = exam_users[0].id
                else:
                    ex_user = None
                if examine['Result'] == u'同意':
                    result = u'同意'
                elif examine['Result'] == u'不同意':
                    result = u'不同意'
                else:
                    pass

                examine_dict = {'user_id':ex_user,'result':result,'recruitment_id': recruit,'date':examine['Time']}
                examine_model.create(examine_dict)
        return 'success'


class Resume(http.Controller):
    @http.route('/resume_import', type='http', auth='public', methods=['POST','GET'])
    def resume_import(self):
        r = requests.get('http://123.56.147.94/talents/get_all_resume_and_interview/')
        datas = r.json()
        for data in datas:
            # print '--' * 80
            # print data['CandidateName'], data['CandidateSex'], data['CandidateAge'], data['CandidateProfile'], data[
            #     'Candidate_edu']
            # print data['CandidatePhone'], data['CandidateEmail'], data['PositionName'], data['Status'], data['UserID']
            resume_dict = {'name': data['CandidateName'].strip() if data['CandidateName'] else data['CandidateName'],
                           'age': data['CandidateAge'].strip(),
                           'work_age': data['CandidateProfile'],
                           'phone': data['CandidatePhone'], 'email': data['CandidateEmail'].strip(),
                           'job': data['PositionName'].strip() if data['PositionName'] else data['PositionName']}
            if data['CandidateSex']:
                gender = data['CandidateSex']
                if gender == u'男':
                    gender = u'male'
                    resume_dict['gender'] = gender
                elif gender == u'女':
                    gender = u'female'
                    resume_dict['gender'] = gender
            if data['Candidate_edu']:
                edu = re.sub(r'\d+', '', data['Candidate_edu']).strip()
                if edu in [u'大专']:
                    edu = u'专科'
                if edu in [u'专科', u"本科", u"硕士", u"博士", u"专升本", u"高级技工", u"高中"]:
                    resume_dict['education'] = edu
            if data['Status']:
                status = data['Status']
                if status == u'未处理':
                    status = u'简历库中'
                resume_dict['state'] = status

            resume_obj = http.request.env['nantian_erp.resume'].sudo().create(resume_dict)
            interviews = data['interview']
            if interviews:
                for interview in interviews:
                    # print '##' * 80
                    # print interview['InterviewResults'].strip()
                    # print interview['Notes'], interview['user'], interview['handletime'][:10] if interview[
                    #     'handletime'] else None, interview['InterStatus']
                    inter_dict = {'review': interview['InterviewResults'].strip(),
                                  'date': interview['handletime'][:10] if interview['handletime'] else None}
                    # if interview['user']:
                    #     inter_dict['interviewer'] = interview['user']
                    if interview['InterStatus'] == u'通过':
                        inter_dict['result'] = 'agree'
                    if interview['InterStatus'] ==u'淘汰':
                        inter_dict['result'] = 'disagree'
                    inter_dict['resume_id'] = resume_obj.id
                    if interview['user']:
                        user = http.request.env['res.users'].sudo().search([('name', '=', interview['user'])], limit=1)
                        if user:
                            inter_dict['interviewer'] = user.id
                    interview_obj = http.request.env['nantian_erp.interview'].sudo().create(inter_dict)
            # offers = data['offer']
            # for offer in offers:
                # print '!!' * 80
                # print offer['Ephone'], offer['Email'].strip(), offer['Eentrytime'], offer['Epost'], offer['Epostgrade'], offer[
                #     'Ejob'], offer['Ejobin'], offer['Ejobaim']
                # print offer['Eprimary'], offer['Esecond'], offer['Eproject'], offer['Ecompacttime'], offer[
                #     'Eapplytime'], offer['handleuser']
                # offer_dict = {'phone':offer['Ephone'],'email':offer['Ecompacttime'].strip(),'contract_time':offer['Email'],'test_time':offer['Eapplytime']}
                # offer_obj = http.request.env['nantian_erp.offer_information'].sudo().create(offer_dict)
        return 'success'

class Hr(http.Controller):
    @http.route('/identification_show', type='http', auth='public', methods=['GET'])
    def identification_show(self, **post):
        hr_id = post['id']
        if hr_id:
            hr = http.request.env['hr.employee'].sudo().search([('id', '=', hr_id)],limit=1)
            uid = http.request.env.uid

            res_objs = http.request.env['ir.model.data'].sudo().search([('name','in',['group_hr_assistant','group_hr_manager_assistant','group_nantian_header','group_hr_recruitment','group_nantian_server_sale_before','group_hr_manager'])])
            groups_ids = [res.res_id for res in res_objs]
            result = http.request.env['res.users'].sudo().search(['|',('id','=',hr.user_id.id),('groups_id.id', 'in', groups_ids),('id','=',uid)])
            if result:
                return 'show'
        return 'hidden'


