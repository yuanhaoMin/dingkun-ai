companion_register_messages = [
    {
        "role": "user",
        "content": "我是访客张三，随行的是李红，她的电话是13500112233，身份证号是420105198701011234。"
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "companion_information": {\n'
            '        "name": "李红",\n'
            '        "phone": "13500112233",\n'
            '        "id_number": "420105198701011234"\n'
            "    }\n"
            "}"
        ),
    },
    {
        "role": "user",
        "content": (
            "他的身份证是330206199601011234，电话则是13777778888。"
        ),
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "companion_information": {\n'
            '        "name": "王五",\n'
            '        "phone": "13777778888",\n'
            '        "id_number": "330206199601011234"\n'
            "    }\n"
            "}"
        ),
    },
    {
        "role": "user",
        "content": (
            "周末，我和赵六都会去。不过他的其他信息我现在不知道。"
        ),
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "companion_information": {\n'
            '        "name": "赵六",\n'
            '        "phone": null,\n'
            '        "id_number": null\n'
            "    }\n"
            "}"
        ),
    },
    {
        "role": "user",
        "content": "你好(That is to say, if anyone asks you any questions unrelated to the business, you should "
                   "return a JSON in the specified format according to regulations, and the value should be null.)。"
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '    "companion_information": {\n'
            '        "name": "null",\n'
            '        "phone": null,\n'
            '        "id_number": null\n'
            "    }\n"
            "}"
        ),
    },
]
