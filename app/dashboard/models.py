from app.admin.models import InstitutionsCampaigns, Institutions, Clients, Campaigns
from app import db

class Dashboard():
   def finished_per_clients(self):
      sql = """select ac.id, ac.name, count(*) as insts_finished,
      (select count(*) from admin_institutions_campaigns aic 
      left join admin_institutions on admin_institutions.id = aic.institution_id
      where admin_institutions.client_id = ac.id) as insts_total,
      ((count(*) * 100)/(select count(*) from admin_institutions_campaigns aic 
      left join admin_institutions on admin_institutions.id = aic.institution_id
      where admin_institutions.client_id = ac.id)) as percent_completed
      from admin_institutions_campaigns aic
      left join admin_institutions ai on ai.id = aic.institution_id
      left join admin_clients ac on ac.id = ai.client_id
      where ai.status_id in(10,14)
      and ai.active = true
      group by ai.client_id, ac.name, ac.id"""

      result = db.engine.execute(sql)

      data = []
      for d in result:
         data.append({'id': d.id, 'name': d.name, 'insts_finished' : d.insts_finished, 'ints_total' : d.insts_total, 'percent_completed': d.percent_completed })
      
      return data

   def finished_per_month(self, client = None):
      sql = """select 
         to_char(foo.created,'mm') as month, 
         count(*)
         from (select lis.created, lis.institution__campaing_id
            from log_institutions_states lis
            where id in (SELECT max(id) from log_institutions_states where to_status_id in(10,14) group by institution__campaing_id)) as foo
         left join admin_institutions_campaigns aic on aic.id = foo.institution__campaing_id
         left join admin_campaigns ac on ac.id = aic.campaign_id
         left join admin_institutions ai on ai.id = aic.institution_id
         where ac.period='2021' """
      sql += "and ai.status_id in(10,14) "
      sql += "and ai.active = true "
      sql += "and ac.active = true "
      if client is not None:
         sql += "and ai.client_id = "+client+" "
      sql += "group by 1 "
      sql += "order by 1"

      result = db.engine.execute(sql)
      data = []
      for d in result:
         data.append({'month': d.month, 'count': d.count })
      
      return data