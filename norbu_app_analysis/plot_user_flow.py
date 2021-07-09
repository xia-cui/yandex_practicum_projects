#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd


# In[ ]:


import plotly.graph_objects as go


# In[ ]:


def filter_starting_step(x, starting_step, n_steps):
    """
    Function used to return the first n_steps for each user starting from the "starting_step".
    The function will be used to generate the event sequence journey for each user.
    """
    starting_step_index = x.index(starting_step)

    return x[starting_step_index: starting_step_index + n_steps]


def user_journey(events, starting_step, n_steps=3, events_per_step=5):
    """
    Function used to map out the journey for each user starting from the defined "starting_step" and count
    how many identical journeys exist across users.
    """
    # sort events by time
    events = events.sort_values(['user_pseudo_id', 'datetime'])
    # find the users that have performed the starting_step
    valid_ids = events[events['event_name'] ==
                       starting_step]['user_pseudo_id'].unique()

    # plan out the journey per user, with each step in a separate column
    flow = events[(events['user_pseudo_id'].isin(valid_ids))]         .groupby('user_pseudo_id')         .event_name.agg(list)         .to_frame()['event_name']         .apply(lambda x: filter_starting_step(x, starting_step=starting_step, n_steps=n_steps))         .to_frame()['event_name'].apply(pd.Series)

    # fill NaNs with "End" to denote no further step by user; this will be filtered out later
    flow = flow.fillna('End')

    # add the step number as prefix to each step
    for i, col in enumerate(flow.columns):
        flow[col] = '{}: '.format(i + 1) + flow[col].astype(str)

    # replace events not in the top "events_per_step" most frequent list with the name "Other"
    # this is done to avoid having too many nodes in the sankey diagram
    for col in flow.columns:
        all_events = flow[col].value_counts().index.tolist()
        all_events = [e for e in all_events if e != (str(col + 1) + ': End')]
        top_events = all_events[:events_per_step]
        to_replace = list(set(all_events) - set(top_events))
        flow[col].replace(to_replace, [str(col + 1) + ': Other']
                          * len(to_replace), inplace=True)

    # count the number of identical journeys up the max step defined
    flow = flow.groupby(list(range(n_steps)))         .size()         .to_frame()         .rename({0: 'count'}, axis=1)         .reset_index()

    return flow


def sankey_df(events, starting_step, n_steps=3, events_per_step=5):
    """
    Function used to generate the dataframe needed to be passed to the sankey generation function.
    "source" and "target" column pairs denote links that will be shown in the sankey diagram.
    """
    # generate the user user flow dataframe
    flow = user_journey(events, starting_step, n_steps, events_per_step)

    # create the nodes labels list
    label_list = []
    cat_cols = flow.columns[:-1].values.tolist()
    for cat_col in cat_cols:
        label_list_temp = list(set(flow[cat_col].values))
        label_list = label_list + label_list_temp

    # create a list of colours for the nodes
    # assign 'blue' to any node and 'grey' to "Other" nodes
    colors_list = ['blue' if i.find(
        'Other') < 0 else 'grey' for i in label_list]

    # transform flow df into a source-target pair
    for i in range(len(cat_cols) - 1):
        if i == 0:
            source_target_df = flow[[cat_cols[i], cat_cols[i + 1], 'count']]
            source_target_df.columns = ['source', 'target', 'count']
        else:
            temp_df = flow[[cat_cols[i], cat_cols[i + 1], 'count']]
            temp_df.columns = ['source', 'target', 'count']
            source_target_df = pd.concat([source_target_df, temp_df])
        source_target_df = source_target_df.groupby(
            ['source', 'target']).agg({'count': 'sum'}).reset_index()

    # add index for source-target pair
    source_target_df['source_id'] = source_target_df['source'].apply(
        lambda x: label_list.index(x))
    source_target_df['target_id'] = source_target_df['target'].apply(
        lambda x: label_list.index(x))

    # filter out the end step
    source_target_df = source_target_df[(~source_target_df['source'].str.contains('End')) &
                                        (~source_target_df['target'].str.contains('End'))]

    return label_list, colors_list, source_target_df


def plot_user_flow(events, starting_step, n_steps=3, events_per_step=5, title='Sankey Diagram'):
    """
    Function used to generate the sankey plot for user journeys.
    """
    # transform raw events dataframe into  source:target pairs including node ids and count of each combination
    label_list, colors_list, source_target_df = sankey_df(
        events, starting_step, n_steps, events_per_step)

    # creating the sankey diagram
    data = go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            color=colors_list,
            line=dict(
                color="black",
                width=0.5
            ),
            label=label_list
        ),
        link=dict(
            source=source_target_df['source_id'].values.tolist(),
            target=source_target_df['target_id'].values.tolist(),
            value=source_target_df['count'].astype(int).values.tolist(),
            hoverlabel=dict(
                bgcolor='#C2C4C7')
        )
    )

    # set window width so that steps are evenly spaced out
    if n_steps < 5:
        width = None
    else:
        width = n_steps * 250

    layout = dict(
        height=600,
        width=width,
        margin=dict(t=30, l=0, r=0, b=30),
        title=title,
        font=dict(
            size=10
        )
    )

    fig = go.Figure(data=[data], layout=layout)
    return fig.show()

