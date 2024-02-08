
function SVMModel = profiler(name)
    rawprdata = readtable(name);
    rawprdata.Properties.VariableNames = ["DATETIME","CPU","RAM","RDISK","WDISK","TOTALTIME"];
    rawprdata = rmmissing(rawprdata);

    Y = [datestr(rawprdata.DATETIME)];
    X = [rawprdata.CPU rawprdata.RAM rawprdata.RDISK rawprdata.WDISK];
    
    SVMModel = fitcecoc(X,Y);
    
    %classificationLearner(X,Y)
    %prdata = removevars(rawprdata,{'DATETIME','TOTALTIME'});
    %prdata
end
