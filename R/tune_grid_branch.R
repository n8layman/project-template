tune_grid_branch <- function(workflow, 
                             params, 
                             training_data_folds, 
                             response = "co_v_final_results",
                             metrics = metric_set(pr_auc,           # Precision-Recall AUC
                                                  roc_auc,          # ROC AUC
                                                  accuracy,         # Accuracy
                                                  f_meas,           # F1 Score
                                                  recall,           # Recall
                                                  precision)) {
  
  # 2D:
  # Add in dynamic response variable and fix the problem with as.factor
  performance <- pmap_dfr(training_data_folds, function(splits, id) {
    map_dfr(1:nrow(params), function(i) {
      
      # Fit the model against the training data
      mod_fit <- workflow |>
        finalize_workflow(params[i,]) |>
        fit(data = training(splits))

      # Predict co_v_final_results and calculate performance metrics
      bind_cols(id = id, params[i,], augment(mod_fit, testing(splits) |> mutate(co_v_final_results = as.factor(co_v_final_results))) |>
        metrics(co_v_final_results, .pred_Positive, estimate = .pred_class))
      })
    })
      
  performance
}

select_best_params <- function(tuned, metric = "roc_auc") {
  
  # Identify the columns that contain the hyper-parameter values
  param_names <- tuned |> select(-id, -starts_with(".")) |> names()
  
  # Group by hyper-parameter values
  # Summarize the .metric.
  tuned |> 
    filter(.metric == metric) |> 
    group_by(across(all_of(param_names)), .metric) |> 
    summarize(.estimate = mean(.estimate, na.rm = T), .groups = "drop") |>
    slice_min(.estimate) |>
    select(-starts_with("."))
}
