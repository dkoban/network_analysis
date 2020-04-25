library(igraph)
library(dplyr)

#################################
# Unresolved Network Interactions
#################################
el <- tibble(source = c("Barak", "Trump", "Obama", "Clinton"),
             target = c("Donald", "Bush", "Clinton", "George"))

g0 <- graph_from_data_frame(el)
party_df <- tibble(name = c("Barak", "Clinton", "Obama", 
                            "Trump", "George", "Donald", "Bush"),
                   party = c("Democrat", "Democrat", "Democrat", 
                             "Republican", "Republican", "Republican", "Republican"))
nl <- data_frame(name = V(g0)$name)
nl <- nl %>% left_join(party_df, by = "name") %>%
  mutate(color = if_else(party == "Republican", "red", "blue"),
         shape = if_else(party == "Republican", "circle", "square"))
V(g0)$color <- nl$color
V(g0)$shape <- nl$shape
plot(g0, vertex.size = 10, vertex.label.dist = 3, 
     edge.arrow.size = 0.5, main = "Unresolved Graph")

##################
# Resolve Entities
##################
name_info <- tibble(first_name = c("Donald", "Donald",  
                                   "Barak", "Barak", 
                                   "George", "George",
                                   "William", "William"),
                    other_name = c("John", "Trump", 
                                   "Hussein", "Obama",
                                   "Walker", "Bush",
                                   "Jefferson", "Clinton"))
g1 <- graph_from_data_frame(name_info)
entity_list <- tibble(entity_id = components(g1)$membership,
                      name = names(components(g1)$membership))
entity_list_collapsed <- entity_list %>% left_join(party_df, by = "name") %>%
  group_by(entity_id) %>%
  summarize(name = paste0(name, collapse = " "),
            party = paste0(party %>% unique() %>% na.omit(), collapse = ", "))
plot(g1, vertex.size = 10, vertex.label.dist = 3, 
     edge.arrow.size = 0.5, main = "Entity Resolution")

###############################
# Resolved Network Interactions
###############################
transformed_el <- el %>% 
  left_join(entity_list, by = c("source" = "name")) %>% rename(source_entity_id = entity_id) %>%
  left_join(entity_list, by = c("target" = "name")) %>% rename(target_entity_id = entity_id) 
g2 <- graph_from_data_frame(transformed_el %>% select(source_entity_id, target_entity_id))
nl <- data_frame(entity_id = V(g2)$name %>% as.integer())
nl <- nl %>% left_join(entity_list_collapsed, by = c("entity_id")) %>%
  mutate(color = if_else(party == "Republican", "red", "blue"),
         shape = if_else(party == "Republican", "circle", "square"))
V(g2)$color <- nl$color
V(g2)$shape <- nl$shape

par(mfrow=c(1,3))
plot(g0, vertex.size = 10, vertex.label.dist = 3, edge.arrow.size = 0.5, main = "Unresolved Graph")
plot(g1, vertex.size = 10, vertex.label.dist = 3, edge.arrow.size = 0.5, main = "Entity Resolution")
plot(g2, vertex.size = 10, vertex.label.dist = 3, edge.arrow.size = 0.5, main = "Resolved Graph")