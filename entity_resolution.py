import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#################################
# Unresolved Network Interactions
#################################
el = pd.DataFrame({'source': ['Barak', 'Trump', 'Obama', 'Clinton'],
                   'target': ['Donald', 'Bush', 'Clinton', 'George']})
g0 = nx.from_pandas_edgelist(el)
party_df = pd.DataFrame({'name': ['Barak', 'Clinton', 'Obama', 
                                  'Trump', 'George', 'Donald'],
                         'party': ['Democrat', 'Democrat', 'Democrat', 
                                   'Republican', 'Republican', 'Republican']})
nl = pd.DataFrame({'name': list(g0.nodes)})
nl = nl.merge(party_df, how = 'left', on = 'name')
nl = nl.assign(
        node_color = lambda df: df['party'].map(
                     lambda party: 'red' if party == 'Republican' else 'blue'),
        node_shape = lambda df: df['party'].map(
                     lambda party: 'o' if party == 'Republican' else 'd'))
node_attr = nl.set_index('name').to_dict('index')        
nx.set_node_attributes(g0, node_attr)
nx.draw(g0, with_labels = True, node_size = 200, node_color = nl['node_color'].tolist())
plt.title("Unresolved Graph")

##################
# Resolve Entities
##################
name_info = pd.DataFrame({'first_name': ['Donald', 'Donald',
                                         'Barak', 'Barak',
                                         'George', 'George',
                                         'William', 'William'],
                          'other_name': ['John', 'Trump',
                                         'Hussein', 'Obama',
                                         'Walker', 'Bush',
                                         'Jefferson', 'Clinton']})
g1 = nx.from_pandas_edgelist(name_info, source = 'first_name', target = 'other_name')
components = [comp for comp in nx.connected_components(g1)]
component_size = [len(comp) for comp in components]
df = []
for value in range(0,len(components)):
    df.append(pd.DataFrame({'entity_id': np.repeat(value + 1,component_size[value]),
                            'name': list(components[value])}))
entity_list = pd.concat(df).reset_index(drop=True)
entity_list_collapsed = entity_list.merge(party_df, how = 'left', on = 'name')
names = entity_list_collapsed.groupby('entity_id')['name'].agg(
        lambda x: ' '.join(set(x))).reset_index()
parties = entity_list_collapsed[entity_list_collapsed['party'].notnull()].groupby(
        'entity_id')['party'].agg(lambda x: ' '.join(set(x))).reset_index()
entity_list_collapsed = names.merge(parties, how = 'left', on = 'entity_id')
nx.draw(g1, with_labels = True, node_size = 200)
plt.title("Entity Resolution")

###############################
# Resolved Network Interactions
###############################
transformed_el = el.merge(entity_list, how = 'left', left_on = 'source', right_on = 'name')
transformed_el.rename(columns = {'entity_id': 'source_entity_id'}, inplace = True)
transformed_el = transformed_el.drop(['name'], axis = 1)
transformed_el = transformed_el.merge(entity_list, how = 'left', left_on = 'target', right_on = 'name')
transformed_el.rename(columns = {'entity_id': 'target_entity_id'}, inplace = True)
transformed_el = transformed_el.drop(['name'], axis = 1)
g2 = nx.from_pandas_edgelist(transformed_el, source = 'source_entity_id', target = 'target_entity_id')
nl = pd.DataFrame({'entity_id': list(g2.nodes)})
nl = nl.merge(entity_list_collapsed, how = 'left', on = 'entity_id')
nl = nl.assign(
        node_color = lambda df: df['party'].map(
                     lambda party: 'red' if party == 'Republican' else 'blue'),
        node_shape = lambda df: df['party'].map(
                     lambda party: 'o' if party == 'Republican' else 'd'))

nx.draw(g2, with_labels = True, node_size = 200, node_color = nl['node_color'].tolist())
