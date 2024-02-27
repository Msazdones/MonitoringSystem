#!/bin/bash

pythonexe="python3"

learning_dir="./learning_and_detection"
svmtrainer="${learning_dir}/SVM_profilerstandaloneApplication/run_SVM_profiler.sh"
svm_output_dir="${learning_dir}/models/SVM/"
iforest_output_dir="${learning_dir}/models/iforest/"
iforesttrainer="${learning_dir}/iforest_profilerstandaloneApplication/run_iforest_profiler.sh"
matlab_dependencies="/usr/local/MATLAB/R2023b/"

python_dir="./data_adaptation"
parser_file="${python_dir}/data_parser.py"
training_file="${python_dir}/train_model.py"

aviable_algs="all svm iforest"]

while getopts o:s:c:pt:h flag
do
    case "${flag}" in
        o)  
            if test -d "${OPTARG}"
            then            
                output_dir=${OPTARG}
            else
                echo "Error. No such a directory: ${OPTARG}."
                exit 1
            fi
            ;;
        s)           
            if [[ ${OPTARG} ]] && [ ${OPTARG} -eq ${OPTARG} 2>/dev/null ]
            then
                step=${OPTARG}
            else
                echo "Error. ${OPTARG} is not an integer or not defined"
                exit 1
            fi
            ;;
        c)  
            clientid=${OPTARG}
            ;;
        p)
            parse=true
            ;;
        t)
            [[ $aviable_algs =~ (^|[[:space:]])${OPTARG}($|[[:space:]]) ]] && trainmode=${OPTARG} || trainmode="null";  
            if [ $trainmode == "null" ] 
            then
                echo "Error. Bad training mode selected."
                exit 1
            fi
            ;;    
        h)
            echo "help"
            exit 1
            ;;
        ?)
            echo "Error. The selected options need arguments."
            exit 1
        (-*) 
            echo "Error. $0: Unrecognized option $1" 1>&2
            exit 1
            ;;
    esac
done

if [ -v parse ]
then
    if [ -z output_dir ] 
    then
        echo "Error: The output path must be set."
        exit 1
    fi
    $pythonexe $parser_file $output_dir $step $clientid
fi

if [ -v trainmode ]
then
    if [ -z output_dir ] 
    then
        echo "Error: The data directory path must be set."
        exit 1
    fi

    file_list=( $output_dir* )
    cnt=0
    for i in "${file_list[@]}"
    do
        echo  "$(( cnt++ ))) $(basename $i)"
    # or do whatever with individual element of the array
    done |xargs -L5 |column -t

    echo ${file_list[0]}

    echo 
    read -a tr_target -p "Select an input file (you can type more than one separated by space, but be careful if you choose to much items): " 

    for tg in "${tr_target[@]}"
    do
        if [ $trainmode == "svm" ]
        then
            $svmtrainer $matlab_dependencies ${file_list[tg]} ${svm_output_dir}
        elif [ $trainmode == "iforest" ]
        then
            $iforesttrainer $matlab_dependencies ${file_list[tg]} ${iforest_output_dir}
        elif [ $trainmode == "all" ]
        then
            $svmtrainer $matlab_dependencies ${file_list[tg]} ${svm_output_dir}
            $iforesttrainer $matlab_dependencies ${file_list[tg]} ${iforest_output_dir}
        fi
    done
fi 




