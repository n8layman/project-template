get_connected_targets <- function(target_raw, mode = "downstream") {
  # Maybe make faster like tar_glimpse?
  if(!mode %in% c("upstream", "downstream")) stop("mode must be either 'upstream' or 'downstream'")
  mode <- ifelse(mode == "upstream", "in", "out")
  network <- targets::tar_network(targets_only = T)
  g <- igraph::graph_from_data_frame(d = network$edges, directed = T)
  connections <- igraph::all_simple_paths(g, target_raw, mode = mode) # This is downstream targets. “in” is upstream
  connected_targets = unlist(connections) |> names() |> unique()
  connected_targets
}
