function prettyJson(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

function clear_in()
{
    document.getElementById('input').value = "";
    document.getElementById('output').value = "";
}
function clear_out()
{
    document.getElementById('output').value = "";
}
function tfunc(request)
{
    console.log("into tfunc request")
    if (request.value.replace(/ /g, "") == "")
    {
        console.log("request is None")
        document.getElementById('output').innerHTML = "请输入非空的请求";
        alert( "请输入非空的请求")
        return;
    }
    // debug
    // console.log("output.text write")
    // document.getElementById('output').innerHTML = prettyJson(request.value)
    // return ;
    var xmlhttp;
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200)
        {
            var info = xmlhttp.responseText;
            document.getElementById('output').innerHTML = prettyJson(info);
            ret = JSON.parse(info)
            console.log(ret)
            if (ret['err_code'] == 100) { tdisconnect() }
        }
    }
    xmlhttp.open('GET', '/send/'+request.value, true)
    xmlhttp.send()
}

function fastaction()
{
    var xmlhttp;
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200)
        {
            var info = xmlhttp.responseText;
            names = info.split(' ');
            htmls = "";
            for(i=0; i<names.length; i++)
            {            
                value = names[i];
                htmls += '<input type="button" onclick="gen_action(value)" id="act_button" value="'
                htmls += value
                htmls += '">\n'
            }
            document.getElementById('template_actions').innerHTML = htmls;
        }
    }
    xmlhttp.open('GET', '/fastaction', true)
    xmlhttp.send()
}

function gen_action(info)
{
    var xmlhttp;
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200)
        {
            var action = xmlhttp.responseText;
            document.getElementById('input').value = action;
        }
    }
    xmlhttp.open('GET', '/getaction/'+info, true)
    xmlhttp.send()

}

function tdisconnect()
{
    var xmlhttp;
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function()
    {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200)
        {
            alert("断开连接!")    
            document.getElementById('conn_button').disabled = false;
            document.getElementById('disconn_button').disabled = true;
        }
    }
    xmlhttp.open('GET', '/disconnect', true)
    xmlhttp.send()
}

function tconnect(host, port)
{
    var xmlhttp;
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200)
        {
            var info = xmlhttp.responseText;
            if (info == 'Success') {
                alert("连接成功!")
                document.getElementById('conn_button').disabled = true;
                document.getElementById('disconn_button').disabled = false;
            }
            else {
                alert("连接失败!"+ info)
                document.getElementById('conn_button').disabled = false;
                document.getElementById('disconn_button').disabled = true;
                // document.getElementById('conn_button').value = info;
            } 
        }
    }
    xmlhttp.open('GET', '/connect/'+host.value+':'+port.value, true)
    xmlhttp.send()
    document.getElementById('conn_button').disabled = true;
}















