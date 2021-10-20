# -*- coding: utf-8 -*-
{
  "name"                 :  "NMC Service Center",
  "summary"              :  "Repair module enhancement",
  "category"             :  "Manufacturing",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Media Engagers",
  "website"              :  "https://www.mediaengagers.com",
  "description"          :  "Manage repairing",
  "depends"              :  ['industry_fsm','warranty'],
  "data"                 :  [
                             'views/project_task.xml',
                             'views/res_config.xml',
                             'views/repair_category.xml',
                             'security/ir.model.access.csv',
                             #'report/repair_templates_repair_oder.xml',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "pre_init_hook"        :  "pre_init_check",
}
