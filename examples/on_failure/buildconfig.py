from wosit.builder import addRule

# Rule that will fail
addRule(
    target = "all",
    command = """
        exit 1  # This command will fail
    """,
    on_failure_command = """
        echo 'Fallback executed due to failure'
    """
)

addRule(
    target = "fail",
    command = """
        exit 1  # This command will fail
    """
)