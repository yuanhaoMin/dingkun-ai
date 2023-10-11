show_zoomed_area_content = '''可以对区域进行标记，标记之后只需点击标记点的名称或者跟我说标记点的名称，就可以直接查看做了标记的区域了；

创建标记点的方法：

步骤1 点击实时轨迹中的标记点按钮，弹窗出标记点列表，此时鼠标是带标记符号的，如下图所示；

![image](http://192.168.1.206:9090/helper-qa/%E6%A0%87%E8%AE%B0%E6%8C%87%E5%AF%BC%E6%AD%A5%E9%AA%A41.png)

步骤2 只要在地图上点击您想要标记的位置，如下图所示；

![image](http://192.168.1.206:9090/helper-qa/%E6%A0%87%E8%AE%B0%E6%8C%87%E5%AF%BC%E6%AD%A5%E9%AA%A42.png)

步骤3 给标记点命名，即可完成标记，示意图如下所示；

![image](http://192.168.1.206:9090/helper-qa/%E6%A0%87%E8%AE%B0%E6%8C%87%E5%AF%BC%E6%AD%A5%E9%AA%A43.png)


'''
building_person_info ='''步骤1 鼠标在目标建筑物上单击右键，出来2d按钮，如下图所示：

![image](http://127.0.0.1:9090/helper-qa/建筑楼内人员情况1.png)

步骤2 点击2d按钮，弹窗出目标建筑物楼层的平面地图，地图可放大缩小拖拽，如下图所示：

![image](http://127.0.0.1:9090/helper-qa/建筑楼内人员情况2.png)

步骤3 鼠标触碰到楼层按钮，显示该楼层的总人数，如下图所示：

![image](http://127.0.0.1:9090/helper-qa/建筑楼内人员情况3.png)

'''
global_dict_array = [
    {
        "route": 'Track',
        "operation": 'view_individual_real_time_track',
        "text": '查看特定人员实时轨迹',
        "name": None,
        "scope": 'Global',
    },
    {
        "route": 'OneClickSearch',
        "operation": 'all_in_one_search',
        "text": '一键搜索人员标签车辆部门',
        "scope": 'Global',
    },
    {
        "route": 'OneClickSearch',
        "operation": 'all_in_one_search',
        "text": '一键搜索人员',
        "scope": 'Global',
    },
    {
        "route": 'OneClickSearch',
        "operation": 'all_in_one_search',
        "text": '一键搜索标签',
        "scope": 'Global',
    },
    {
        "route": 'OneClickSearch',
        "operation": 'all_in_one_search',
        "text": '一键搜索车辆',
        "scope": 'Global',
    },
    {
        "route": 'OneClickSearch',
        "operation": 'all_in_one_search',
        "text": '一键搜索部门',
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'view_individual_real_time_track',
        "text": '查看特定人员位置',
        "name": None,
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'view_individual_history_track',
        "text": '查询人员的历史轨迹',
        "name": None,
        "start_time": None,
        "end_time": None,
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'view_individual_final_location',
        "text": '查询人员的最终位置',
        "name": None,
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'view_individual_detail',
        "text": '我想看看某个人员的详细信息',
        "name": None,
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'view_online_individual_list',
        "text": '查看在线人员列表',
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'view_offline_individual_list',
        "text": '查看离线人员列表',
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'view_online_vehicle_list',
        "text": '查看在线车辆列表',
        "scope": 'Global',
    },
    {
        "route": 'Help',
        "operation": 'navigate_to_help_center',
        "text": '跳转到帮助中心',
        "scope": 'Global',
    },
    {
        "route": 'Screen',
        "operation": 'navigate_to_Screen',
        "text": '跳转到数据大屏',
        "scope": 'Global',
    },
    {
        "route": 'Track',
        "operation": 'navigate_to_Track',
        "text": '跳转到轨迹页面',
        "scope": 'Global',
    },
    {
        "route": 'OneClickSearch',
        "operation": 'navigate_to_one_search',
        "text": '跳转到一键搜索页面',
        "scope": 'Global',
    },
    {
        "route": 'Screen',
        "operation": 'close_chart',
        "text": '关闭列表',
        "scope": 'Global',
    },
]

screen_dict_array = [
    {
        "route": 'Screen',
        "operation": 'display_alarm_detail_list',
        "text": '展示告警详情列表',
        "start_time": None,
        "end_time": None,
        "page": None,
        "listRows": None,
        "scope": 'Screen',
    },
    {
        "route": 'Screen',
        "operation": 'view_inspection_trend',
        "text": '展开巡检趋势',
        "start_time": None,
        "end_time": None,
        "page": None,
        "listRows": None,
        "scope": 'Screen',
    },
    {
        "route": 'Screen',
        "operation": 'view_visitor_list',
        "text": '展开访客列表',
        "start_time": None,
        "end_time": None,
        "page": None,
        "listRows": None,
        "scope": 'Screen',
    },
    {
        "route": 'Screen',
        "operation": 'next_page',
        "text": '下一页',
        "scope": 'Screen',
    },
    {
        "route": 'Screen',
        "operation": 'previous_page',
        "text": '上一页',
        "scope": 'Screen',
    },
    {
        "route": 'Track',
        "operation": 'navigate_to_Track',
        "text": '返回系统',
        "scope": 'Screen',
    },
]

track_dict_array = [
    {
        "route": 'Track',
        "operation": 'track_individual',
        "text": '追踪人员',
        "name": None,
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'untrack_individual',
        "text": '取消追踪人员',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'stop_tracking',
        "text": '退出追踪',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'start_tracking',
        "text": '定位追踪',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'display_only_individual_track_info',
        "text": '只显示人员轨迹信息',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'view_online_vehicle_list',
        "text": '点击在线总车辆',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'view_online_individual_list',
        "text": '点击在线总人数',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'view_offline_individual_list',
        "text": '点击离线总人数',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'view_offline_vehicle_list',
        "text": '点击离线总车辆',
        "scope": 'Track',
    },
    {
        "route": 'Track',
        "operation": 'return_to_main_perspective',
        "text": '回到主视角',
        "scope": 'Track',
    },

]

help_dict_array = [
    {
        "route": 'Help',
        "operation": 'show_content',
        "text": '查看局部区域情况',
        "content": show_zoomed_area_content,
        "scope": 'Help',
    },
    {
        "route": 'Help',
        "operation": 'show_content',
        "text": '怎么转动地图',
        "content": "按住鼠标右键，可以任意转动地图，按照鼠标左键，可以任意拖拽地图；点击默认视图按钮，可以回到地图的默认视角-顶视图",
        "scope": 'Help',
    },
    {
        "route": 'Track',
        "operation": 'display_only_individual_track_info',
        "text": '地图上显示信息太多，我只想要显示人员轨迹信息',
        "scope": 'Help',
    },
    {
        "route": 'Help',
        "operation": 'view_building_floor_personnel_information',
        "text": '查看建筑物楼层中的人员信息',
        "content": building_person_info,
        "scope": 'Help',
    },
]

