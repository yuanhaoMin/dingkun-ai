from app.util.time_utll import parse_relative_date

visitor_register_messages = [
    {
        "role": "user",
        "content": "我是深圳电力的经理张三，我手机号12345678910。" "我要见市场部的王总。明天时间9点。目的是谈ai的项目。",
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "visitor_information": {\n'
            '        "phone": "12345678910",\n'
            '        "name": "张三",\n'
            '        "id_number": null,\n'
            '        "license_plate": null\n'
            "    },\n"
            '    "visit_details": {\n'
            '        "visited_department": "市场部",\n'
            '        "visited_person": "王总",\n'
            f"        \"appointment_time\": \"{parse_relative_date('明天').strftime('%Y-%m-%d')} 上午\",\n"
            '        "visit_unit": "深圳电力",\n'
            '        "visit_reason": "谈ai的项目"\n'
            "    }\n"
            "}"
        ),
    },
    {
        "role": "user",
        "content": (
            "我是北京科技公司的李四。下周五下午3点，"
            "我要与研发部的赵经理商谈新项目。我的身份证号码是110105198601015678。"
            "车牌号为京A12345。"
        ),
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "visitor_information": {\n'
            '        "phone": null,\n'
            '        "name": "李四",\n'
            '        "id_number": "110105198601015678",\n'
            '        "license_plate": "京A12345"\n'
            "    },\n"
            '    "visit_details": {\n'
            '        "visited_department": "研发部",\n'
            '        "visited_person": "赵经理",\n'
            f"        \"appointment_time\": \"{parse_relative_date('下周五').strftime('%Y-%m-%d')} 下午\",\n"
            '        "visit_unit": "北京科技公司",\n'
            '        "visit_reason": "商谈新项目"\n'
            "    }\n"
            "}"
        ),
    },
    {
        "role": "user",
        "content": (
            "周六我要去上海金融公司，找销售部的张经理。"
            "时间是上午10点。我的名字叫赵六，身份证是330201198701012345。"
            "我没有车。目的是谈合作。"
        ),
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "visitor_information": {\n'
            '        "phone": null,\n'
            '        "name": "赵六",\n'
            '        "id_number": "330201198701012345",\n'
            '        "license_plate": null\n'
            "    },\n"
            '    "visit_details": {\n'
            '        "visited_department": "销售部",\n'
            '        "visited_person": "张经理",\n'
            f"        \"appointment_time\": \"{parse_relative_date('本周六').strftime('%Y-%m-%d')} 上午\",\n"
            '        "visit_unit": "上海金融公司",\n'
            '        "visit_reason": "谈合作"\n'
            "    }\n"
            "}"
        ),
    },
    {"role": "user", "content": "我是陈七，下午要见技术部的杨总。"},
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "visitor_information": {\n'
            '        "phone": null,\n'
            '        "name": "陈七",\n'
            '        "id_number": null,\n'
            '        "license_plate": null\n'
            "    },\n"
            '    "visit_details": {\n'
            '        "visited_department": "技术部",\n'
            '        "visited_person": "杨总",\n'
            f"        \"appointment_time\": \"{parse_relative_date('今天').strftime('%Y-%m-%d')} 下午\",\n"
            '        "visit_unit": null,\n'
            '        "visit_reason": null\n'
            "    }\n"
            "}"
        ),
    },
]

for message in visitor_register_messages:
    print(message["content"])
