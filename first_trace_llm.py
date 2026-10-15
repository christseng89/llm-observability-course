from dotenv import load_dotenv
from langfuse.openai import openai

from langfuse import Langfuse, observe, propagate_attributes

# @observe 创建父 span(trace 根节点),里面的 openai 调用自动成为子 generation
load_dotenv()

question = "123 + 456 * 2 = "
name = "first_trace_llm"


@observe(name=name)
def calculate(question: str) -> str:
    # chat.completions.create() 传了 name="first_trace_llm" 和 metadata={...}。
    # 这两个是 Langfuse 扩展的参数
    completion = openai.chat.completions.create(
        name=name,
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a very accurate calculator. You output only the result of the calculation.",
            },
            {"role": "user", "content": question},
        ],
    )
    return completion.choices[0].message.content


# 包住根调用,根 span 和所有子节点都会继承这些属性
# (user_id、tags 是 Langfuse 的真实字段,metadata 也会出现在父 span 上)
with propagate_attributes(
    user_id="user_123",
    tags=["calculator"],
    metadata={"project": name + "_project"},
):
    print(calculate(question))

# 脚本很短,退出前确保数据已发送
Langfuse().flush()
