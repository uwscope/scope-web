import json
import logging


# For debugging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)


def pre_save_remove_output(model, **kwargs):
    """
    Ensure output is not written to disk.

    Based on pre_save example:

    https://jupyter-notebook.readthedocs.io/en/stable/extending/savehooks.html
    """

    # For debugging
    # logging.debug(json.dumps(model))

    # Only run on notebooks
    if model["type"] != "notebook":
        return

    # Only run on nbformat v4
    assert model["content"]["nbformat"] == 4
    if model["content"]["nbformat"] != 4:
        return

    # Review all cells in the notebook
    for cell in model["content"]["cells"]:
        # In every code cell, remove any output
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None


c.FileContentsManager.pre_save_hook = pre_save_remove_output
