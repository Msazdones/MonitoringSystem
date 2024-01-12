server = "127.0.0.1";
port = 27017;
dbname = "test";
collection = "Client_127_0_0_1";

conn = mongoc(server,port,dbname);

if isopen(conn) == 0
    exit;
end

documents = find(conn,collection);

dates = [];
info_PID = [];
info_NAME = [];
info_CPU = [];
info_RAM = [];
info_RDISK = [];
info_WDISK = [];

names = 0;
content = 0;
for i = 1:length(documents)
    names = fieldnames(documents{i});
    dates = [dates names(2)];

    content = struct2cell(documents{i});
    content = content{2};
    aux_PID = [];
    aux_NAME = [];
    aux_CPU = [];
    aux_RAM =[];
    aux_RDISK = [];
    aux_WDISK = [];
    for j = 1:length(content)
        aux_PID = [aux_PID content{j}.pid];
        aux_NAME = [aux_NAME content{j}.name];
        aux_CPU = [aux_CPU content{j}.CPU];
        aux_RAM = [aux_RAM content{j}.RAM];
        aux_RDISK = [aux_RDISK content{j}.RDISK];
        aux_WDISK = [aux_WDISK content{j}.WDISK];
    end
    info_PID = [info_PID ; aux_PID];
end



close(conn);