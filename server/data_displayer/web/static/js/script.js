function plot_cpu(yArray, xArray, xlimits)
{
    // Define Data
    const data = [{x: xArray, y: yArray, mode:"lines"}];
    
    // Define Layout
    const layout = {xaxis: {range: xlimits, title: "Time"}, yaxis: {range: [0, 100], title: "Percentage"},   title: "CPU Usage"};

    // Display using Plotly
    Plotly.newPlot("myPlot", data, layout);
}

$(document).ready(function(){
    // sending a connect request to the server.
    var socket = io.connect('http://localhost:5000');
    var hactive = null;

    socket.emit('host_list', {data: 'get_hosts'});

    socket.on('actualize_plots', function(msg, cb) { 
        //console.log("Active" , active)
        plot_cpu(msg.CPU_data, msg.time, msg.time_limit);
       
        socket.emit('host_list', {data: 'get_hosts'});

        if(hactive != null)
        {
            socket.emit('selected_host', {data: hactive[0], eid: hactive[1]});
        }
    });

    socket.on('actualize_host_list', function(msg, cb) {    
        var current_host_list = []
        var new_host_list
        $.each($('#hostList').find('li'), function(i, val){ 
            current_host_list.push(val.firstChild.textContent);
        });
        new_host_list = msg.hosts.filter(n => !current_host_list.includes(n))

        $.each(new_host_list, function(i, val) {
            $('#hostList').append("<li id='h_" + i + "'>" + val + "<ul id='procList_h_" + i + "' class='list-off'></ul></li>");
        });
    });

    socket.on('actualize_proc_list', function(msg, cb) {    
        var current_proc_list = []
        var new_proc_list
        
        var listid = '#procList_' + msg.eid

        $.each($(listid).find('li'), function(i, val){ 
            current_proc_list.push(val.firstChild.textContent);
        });
        new_proc_list = msg.proc_list.filter(n => !current_proc_list.includes(n))
        
        $.each(new_proc_list, function(i, val) {
            $(listid).append("<li id='p_" + i + "'>" + val + "</li>");
        });
        
        $(listid).attr("class", "list-on");
        hactive = [$(listid).parent()[0].firstChild.textContent, $(listid).parent().attr("id")]
    });

    $('#hostList').on("click", "li", function(event){
        var parentid = "#" + $(this).parent().attr("id")
        var rmidlist = []
        var idtorm

        if($("ul", this).attr("class") == "list-on")
        {
            $("ul", this).attr("class", "list-off");
            hactive = null;
        }
        else if($("ul", this).attr("class") == "list-off")
        {
            socket.emit('selected_host', {data: $(this).text(), eid: $(this).attr("id")});
            //console.log($(this).text(), $(this).attr("id"));
        }

        $.each($(parentid).find("li"), function(){
            rmidlist.push($(this).attr("id"));
        }); 
        
        $.each(rmidlist, function(i, val) {
            idtorm = "#" + val + " ul"
            $(idtorm).attr("class", "list-off");
            $(idtorm).empty()
        });
        
    });
});