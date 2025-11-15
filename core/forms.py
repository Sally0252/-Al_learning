from django import forms

# input a request.Post, and choice_data
class ChoiceForm(forms.Form):


    def __init__(self, *args, choice_data=None, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.choice_data = choice_data or []
        
        # 检查问题数据并动态创建字段
        if self.choice_data:
            for i, q_item in enumerate(self.choice_data):
                # 动态生成字段名，例如：'q_0', 'q_1', 'q_2', ...
                field_name = f'q_{i}'
                
                # 动态创建 ChoiceField
                self.fields[field_name] = forms.ChoiceField(
                    # 设置问题的 label
                    label=q_item.get('label', f'问题 {i+1}'),
                    # 设置问题的 choices
                    choices=q_item.get('choices', []),
                    # 设置单选按钮 widget
                    widget=forms.RadioSelect,
                    required=True
                )
