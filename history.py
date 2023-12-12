import streamlit as st
from st_aggrid import AgGrid, JsCode, GridUpdateMode, ColumnsAutoSizeMode

import db_access
from models import XRunDetail, XRun, XConversation

#@st.cache_resource
def load_run_steps():
    return db_access.get_all_as_df(XRunDetail)

def load_runs():
    return db_access.get_all_as_df(XRun)

def load_conversations():
    return db_access.get_all_as_df(XConversation)

def load_history_data():
    all_conversations = load_conversations()
    all_runs = load_runs()
    all_steps = load_run_steps()
    df_r_steps = []
    df_r_num_calls = []
    for index, row in all_runs.iterrows():
        run_steps = all_steps.query(f"run_id == '{row['run_id']}'")
        df_r_steps.append(run_steps)
        df_r_num_calls.append(len(run_steps))

    all_runs["steps"] = df_r_steps
    all_runs["num_events"] = df_r_num_calls

    df_c_runs = []
    df_c_num_runs = []
    df_c_num_events = []
    for index, row in all_conversations.iterrows():
        c_runs = all_runs.query(f"thread_id == '{row['thread_id']}'")
        df_c_runs.append(c_runs)
        df_c_num_runs.append(len(c_runs))
        df_c_num_events.append(c_runs["num_events"].sum())

    all_conversations["runs"] = df_c_runs
    all_conversations["num_runs"] = df_c_num_runs
    all_conversations["num_events"] = df_c_num_events
    return all_conversations

def run() :
    st.set_page_config(page_title="test", layout="wide")

    st.header("Conversation History and Log")

    all_conversations = load_history_data()

    gridOptions = {
        # enable Master / Detail
        "masterDetail": True,
        "rowSelection": "single",
        "tooltipShowDelay": 0,
        "tooltipHideDelay": 2000,
        "detailRowAutoHeight": False,
        "detailRowHeight": 400,
        "pagination": True,
        "paginationAutoPageSize": False,
        "paginationPageSize": 10,
        # the first Column is configured to use agGroupCellRenderer
        "columnDefs": [
            {
                "field": "thread_id",
                "cellRenderer": "agGroupCellRenderer",
                "checkboxSelection": False,
                "tooltipField": "thread_id"
            },
            {"field": "default_assistant_id", "tooltipField": "assistant_id"},
            {"field": "num_runs"},
            {"field": "num_events", "tooltipField": "num_events"},
            {"field": "created_at", "tooltipField": "created_at"},
        ],
        "defaultColDef": {
            "filter": True,
            "sortable": True,
            "cellStyle": {'color': 'black', 'font-size': '15px'},
            "flex": 1,
        },
        # provide Detail Cell Renderer Params
        "detailCellRendererParams": {
            # provide the Grid Options to use on the Detail Grid
            "detailGridOptions": {
                "masterDetail": True,
                "rowSelection": "single",
                "checkboxSelection": False,
                "enableRangeSelection": False,
                "detailRowAutoHeight": True,
                "pagination": True,
                "paginationAutoPageSize": False,
                "paginationPageSize": 5,
                "columnDefs": [
                    {"field": "run_id", "tooltipField": "run_id",
                        "cellRenderer": "agGroupCellRenderer",
                        "checkboxSelection": False,
                     },
                    {"field": "assistant_id", "tooltipField": "assistant_id"},
                    {"field": "thread_id", "tooltipField": "thread_id"},
                    {"field": "num_events", "tooltipField": "num_events"},
                    {"field": "created_at", "tooltipField": "created_at"}
                ],
                "defaultColDef": {
                    "sortable": True,
                    "filter": True,
                    "flex": 1,
                },
                "detailCellRendererParams": {
                    # provide the Grid Options to use on the Detail Grid
                    "detailGridOptions": {
                        "rowSelection": "single",
                        "checkboxSelection": False,
                        "enableRangeSelection": False,
                        "pagination": True,
                        "paginationAutoPageSize": False,
                        "paginationPageSize": 5,
                        "columnDefs": [
                            {"field": "type", "tooltipField": "type"},
                            {"field": "tool", "tooltipField": "tool"},
                            {"field": "input", "tooltipField": "input"},
                            {"field": "output", "tooltipField": "output"},
                            {"field": "created_at", "tooltipField": "created_at"}
                        ],
                        "defaultColDef": {
                            "sortable": True,
                            "flex": 1,
                        },
                    },
                    # get the rows for each Detail Grid;
                    "getDetailRowData": JsCode(
                        """function (params) {
                            console.log(params.data);
                            params.successCallback(params.data.steps);
                }"""
                    ).js_code,
                }
            },
            # get the rows for each Detail Grid;
            "getDetailRowData": JsCode(
                """function (params) {
                    console.log(params);
                    params.successCallback(params.data.runs);
        }"""
            ).js_code,
        },
    }


    r = AgGrid(
        all_conversations,
        gridOptions=gridOptions,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )

if __name__ == "__main__":
    run()