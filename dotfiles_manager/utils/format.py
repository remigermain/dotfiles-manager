def ask(msg: str) -> bool:
    choices_yes = ["y", "yes"]
    choices_no = ["n", "no"]
    choices_join = ", ".join(choices_yes + choices_no)
    while True:
        try:
            result = input(f"{msg} [{choices_join}]\n").strip().lower()
        except KeyboardInterrupt:
            break
        else:
            if result in choices_yes:
                return True
            elif result in choices_no:
                return False
            print(f"invalid choices '{result}'")
