from alt_text_langgraph import create_alt_text_workflow

if __name__ == "__main__":

    # First run
    input1 = "A group of four engineers in hard hats and safety vests discuss blueprints at a construction site."
    workflow = create_alt_text_workflow()
    response1 = workflow.invoke({"user_input": input1
    })
    print(f"Generated: {response1}")

    # Feedback run (simulate user feedback)
    feedback_input = "make it more professional"
    state2 = dict(response1)
    state2["user_input"] = feedback_input
    response2 = workflow.invoke(state2)
    print(f"After feedback: {response2}")

    # Approve run (simulate user approval)
    feedback_input = "approve"
    state3 = dict(response2)
    state3["user_input"] = feedback_input
    response3 = workflow.invoke(state3)
    print(f"After feedback: {response3}")