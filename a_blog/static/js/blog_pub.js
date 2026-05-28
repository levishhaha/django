// 获取页面中的CSRF Token
const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value

// 富文本编辑器的js代码部分
const { createEditor, createToolbar } = window.wangEditor

const editorConfig = {
placeholder: 'Type here...',
onChange(editor) {
    const html = editor.getHtml()
    // console.log('editor content', html)
    // 也可以同步到 <textarea>
},
MENU_CONF: {
    uploadImage: {
        server: '/Blog/blog_image_pub',
        fieldName: 'file',
        headers: {
                'X-CSRFToken': csrftoken
            },
        // 登录校验，需要加上这行携带Cookie
        withCredentials: true
    }
}
}


const editor = createEditor({
    selector: '#editor-container',
    html: '<p><br></p>',
    config: editorConfig,
    mode: 'default', // or 'simple'
})

const toolbarConfig = {}

const toolbar = createToolbar({
    editor,
    selector: '#toolbar-container',
    config: toolbarConfig,
    mode: 'default', // or 'simple'
})




// 按钮提交数据部分
function pub_click(){
    let pub_button = document.getElementById('pub-button')
    pub_button.addEventListener('click',function button_click(event){
        let content = editor.getHtml()
        let title = document.getElementById('title').value
        // console.log(title,content)
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
        $.ajax({
            url: 'blog_pub',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data:{
                content: content,
                title: title,
            },
            success:function(result){
                // console.log('成功了吗')
                if(result['code']==400){
                    alert(result['message'])
                }else{
                    alert(result['message'])
                    let blog_id = result['data']['blog_id']
                    window.location.href = 'blog_detail/'+blog_id
                }
            },
            error: function(err) {
                console.log('请求失败', err)
                alert('网络或服务器异常')
            }
        })
    })
}

pub_click()