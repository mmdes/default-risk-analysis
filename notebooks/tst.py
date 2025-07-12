{
   "XGBoost":{
      "Melhores parâmetros":{
         "clf__colsample_bytree":0.6,
         "clf__gamma":0,
         "clf__learning_rate":0.1,
         "clf__max_depth":10,
         "clf__min_child_weight":1,
         "clf__n_estimators":300,
         "clf__subsample":0.8
      },
      "ROC AUC (validação)":0.9600524212116186,
      "ROC AUC (teste)":0.9685975419379949,
      "Classification Report":{
         "0":{
            "precision":0.977415124581087,
            "recall":0.981275599765945,
            "f1-score":0.97934155777794,
            "support":13672.0
         },
         "1":{
            "precision":0.7521781219748306,
            "recall":0.7148114075436982,
            "f1-score":0.7330188679245283,
            "support":1087.0
         },
         "accuracy":0.9616505183278,
         "macro avg":{
            "precision":0.8647966232779588,
            "recall":0.8480435036548216,
            "f1-score":0.8561802128512341,
            "support":14759.0
         },
         "weighted avg":{
            "precision":0.9608264246804838,
            "recall":0.9616505183278,
            "f1-score":0.9611998975116172,
            "support":14759.0
         }
      },
      "Confusion Matrix":[
         [
            13416,
            256
         ],
         [
            310,
            777
         ]
      ]
   },
   "RandomForest":{
      "Melhores parâmetros":{
         "clf__bootstrap":false,
         "clf__max_depth":"None",
         "clf__max_features":"log2",
         "clf__min_samples_leaf":2,
         "clf__min_samples_split":5,
         "clf__n_estimators":300
      },
      "ROC AUC (validação)":0.9624474982057096,
      "ROC AUC (teste)":0.9665197856684913,
      "Classification Report":{
         "0":{
            "precision":0.9799985293036253,
            "recall":0.9747659449970744,
            "f1-score":0.9773752337648051,
            "support":13672.0
         },
         "1":{
            "precision":0.7025862068965517,
            "recall":0.749770009199632,
            "f1-score":0.7254116599910992,
            "support":1087.0
         },
         "accuracy":0.9581949996612237,
         "macro avg":{
            "precision":0.8412923681000886,
            "recall":0.8622679770983532,
            "f1-score":0.8513934468779522,
            "support":14759.0
         },
         "weighted avg":{
            "precision":0.9595671183369955,
            "recall":0.9581949996612237,
            "f1-score":0.9588181225315224,
            "support":14759.0
         }
      },
      "Confusion Matrix":[
         [
            13327,
            345
         ],
         [
            272,
            815
         ]
      ]
   },
   "LogisticRegression":{
      "Melhores parâmetros":{
         "clf__C":10.0
      },
      "ROC AUC (validação)":0.8597710862099304,
      "ROC AUC (teste)":0.8731729256283229,
      "Classification Report":{
         "0":{
            "precision":0.9774136027850896,
            "recall":0.8419397308367467,
            "f1-score":0.9046327950017683,
            "support":13672.0
         },
         "1":{
            "precision":0.27531857813547955,
            "recall":0.7552897884084636,
            "f1-score":0.4035389530597198,
            "support":1087.0
         },
         "accuracy":0.8355579646317501,
         "macro avg":{
            "precision":0.6263660904602846,
            "recall":0.7986147596226052,
            "f1-score":0.654085874030744,
            "support":14759.0
         },
         "weighted avg":{
            "precision":0.9257043208693686,
            "recall":0.8355579646317501,
            "f1-score":0.867727245425848,
            "support":14759.0
         }
      },
      "Confusion Matrix":[
         [
            11511,
            2161
         ],
         [
            266,
            821
         ]
      ]
   },
   "LightGBM":{
      "Melhores parâmetros":{
         "clf__colsample_bytree":0.6,
         "clf__learning_rate":0.1,
         "clf__min_child_samples":50,
         "clf__n_estimators":300,
         "clf__num_leaves":100,
         "clf__subsample":0.6
      },
      "ROC AUC (validação)":0.9586362715208164,
      "ROC AUC (teste)":0.9687959073211093,
      "Classification Report":{
         "0":{
            "precision":0.9761092150170648,
            "recall":0.9831772966647162,
            "f1-score":0.9796305068687826,
            "support":13672.0
         },
         "1":{
            "precision":0.7672064777327935,
            "recall":0.6973321067157314,
            "f1-score":0.7306024096385542,
            "support":1087.0
         },
         "accuracy":0.9621248052036045,
         "macro avg":{
            "precision":0.8716578463749292,
            "recall":0.8402547016902238,
            "f1-score":0.8551164582536683,
            "support":14759.0
         },
         "weighted avg":{
            "precision":0.9607235333700697,
            "recall":0.9621248052036045,
            "f1-score":0.9612895934133142,
            "support":14759.0
         }
      },
      "Confusion Matrix":[
         [
            13442,
            230
         ],
         [
            329,
            758
         ]
      ]
   }
}