import ua_generator


def generate_user_agent():
    return ua_generator.generate(
        browser="firefox",
        device="desktop",
        platform="linux",
    )
