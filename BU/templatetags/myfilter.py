# coding:utf-8
from django import template
from django.utils.safestring import mark_safe
register = template.Library()


TEMP1 = """
    <div class="media" data-key="{}">
        <span class="media-left" href="#">
            <img class="media-object" src="/uploads/{}" alt="头像">
        </span>
        <div class="media-body">
            <div class="media-heading small text-muted">
                <a href="#">{}</a>-
                <span>{}</span>
                <a data-toggle="collapse" href="" class="answer">回复</a>
            </div>
            <span>{}</span>
            

"""

def generate_comment_html(sub_comment_dic):
    html = ''
    # 遍历子元素
    for k, v_dic in sub_comment_dic.items():
        if k.user:
            html += TEMP1.format(k.id, k.user.avatar, k.user.username, k.date.strftime('%Y-%m-%d %H:%M:%S'), k.content)
        else:
            html += TEMP1.format(k.id, 'avatar/default.png', '匿名', k.date.strftime('%Y-%m-%d %H:%M:%S'), k.content)
        # 假如子元素的值为真,说明有子评论
        if v_dic:
            # 递归处理,直到全部处理完
            html += generate_comment_html(v_dic)
        html += "</div>"
        html += '</div>'

    return html


@register.simple_tag
def comment_tree(comment_dic):
    html = ''
    for k, v in comment_dic.items():
        if k.user:
            html += TEMP1.format(k.id, k.user.avatar, k.user.username, k.date.strftime('%Y-%m-%d %H:%M:%S'), k.content)
        else:
            html += TEMP1.format(k.id, 'avatar/default.png', '匿名', k.date.strftime('%Y-%m-%d %H:%M:%S'), k.content)
        if v:
            # 遍历子元素
            html += generate_comment_html(v)
        html += '</div>'
        html += '</div>'

    return mark_safe(html)