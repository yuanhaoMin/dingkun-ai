show_zoomed_area_content = '''可以对区域进行标记，标记之后只需点击标记点的名称或者跟我说标记点的名称，就可以直接查看做了标记的区域了；

创建标记点的方法：

步骤1 点击实时轨迹中的标记点按钮，弹窗出标记点列表，此时鼠标是带标记符号的，如下图所示；

![image](http://192.168.1.206:9090/helper-qa/%E6%A0%87%E8%AE%B0%E6%8C%87%E5%AF%BC%E6%AD%A5%E9%AA%A41.png)

步骤2 只要在地图上点击您想要标记的位置，如下图所示；

![image](http://192.168.1.206:9090/helper-qa/%E6%A0%87%E8%AE%B0%E6%8C%87%E5%AF%BC%E6%AD%A5%E9%AA%A42.png)

步骤3 给标记点命名，即可完成标记，示意图如下所示；

![image](http://192.168.1.206:9090/helper-qa/%E6%A0%87%E8%AE%B0%E6%8C%87%E5%AF%BC%E6%AD%A5%E9%AA%A43.png)


'''

functions = [
  {
    "route": "Track",
    "operation": "view_individual_real_time_track",
    "text": "查看特定人员实时轨迹",
    "name": None
  },
  {
    "route": "OneClickSearch",
    "operation": "all_in_one_search",
    "text": "一键搜索人员标签车辆部门",
  },
  {
    "route": "OneClickSearch",
    "operation": "all_in_one_search",
    "text": "一键搜索人员",
  },
  {
    "route": "OneClickSearch",
    "operation": "all_in_one_search",
    "text": "一键搜索标签",
  },
  {
    "route": "OneClickSearch",
    "operation": "all_in_one_search",
    "text": "一键搜索车辆",
  },
  {
    "route": "OneClickSearch",
    "operation": "all_in_one_search",
    "text": "一键搜索部门",
  },
  {
    "route": "Track",
    "operation": "view_individual_real_time_track",
    "text": "查看特定人员位置",
    "name": None
  },
  {
    "route": "Track",
    "operation": "view_individual_history_track",
    "text": "查询人员的历史轨迹",
    "name": None,
    "start_time": None,
    "end_time": None
  },
  {
    "route": "Track",
    "operation": "view_individual_final_location",
    "text": "查询人员的最终位置",
    "name": None
  },
  {
    "route": "Track",
    "operation": "view_individual_detail",
    "text": "我想看看某个人员的详细信息",
    "name": None
  },
  {
    "route": "Track",
    "operation": "display_only_individual_track_info",
    "text": "只想要显示人员轨迹信息",
    "name": None
  },
  {
    "route": "Track",
    "operation": "view_online_individual_list",
    "text": "查看在线人员列表"
  },
  {
    "route": "Track",
    "operation": "view_offline_individual_list",
    "text": "查看离线人员列表"
  },
  {
    "route": "Track",
    "operation": "view_online_vehicle_list",
    "text": "查看在线车辆列表"
  },
  {
    "route": "Screen",
    "operation": "display_alarm_detail_list",
    "text": "展示告警详情列表",
    "start_time": None,
    "end_time": None,
    "page": None,
    "listRows": None
  },
  {
    "route": "Screen",
    "operation": "view_inspection_trend",
    "text": "展开巡检趋势",
    "start_time": None,
    "end_time": None,
    "page": None,
    "listRows": None
  },
  {
    "route": "Screen",
    "operation": "view_visitor_list",
    "text": "展开访客列表",
    "start_time": None,
    "end_time": None,
    "page": None,
    "listRows": None
  },
  {
    "route": "Help",
    "operation": "navigate_to_help_center",
    "text": "跳转到帮助中心"
  },
  {
    "route": "Screen",
    "operation": "navigate_to_Screen",
    "text": "跳转到数据大屏"
  },
  {
    "route": "Track",
    "operation": "navigate_to_Track",
    "text": "跳转到轨迹页面"
  },
  {
    "route": "OneClickSearch",
    "operation": "navigate_to_one_search",
    "text": "跳转到一键搜索页面",
  },
  {
    "route": "Screen",
    "operation": "next_page",
    "text": "下一页",
  },
  {
    "route": "Screen",
    "operation": "previous_page",
    "text": "上一页",
  },
  {
    "route": "Track",
    "operation": "track_individual",
    "text": "追踪人员",
    "name": None
  },
  {
    "route": "Track",
    "operation": "untrack_individual",
    "text": "取消追踪人员",
  },
  {
    "route": "Screen",
    "operation": "close_chart",
    "text": "关闭列表",
  },
  {
    "route": "Track",
    "operation": "stop_tracking",
    "text": "退出追踪"
  },
  {
    "route": "Track",
    "operation": "start_tracking",
    "text": "定位追踪"
  },
  {
    "route": "Track",
    "operation": "navigate_to_Track",
    "text": "返回系统"
  },
  {
    "route": "Help",
    "operation": "show_zoomed_area",
    "text": "查看局部区域情况",
    "content": show_zoomed_area_content
  },
]

