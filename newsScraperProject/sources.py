SOURCE_BIAS = {
    "foxnews.com": "right",
    "breitbart.com": "right",
    "nytimes.com": "left",
    "cnn.com": "left",
    "apnews.com": "undetermined",   # example — adjust to your own judgment
    "reuters.com": "undetermined",
    # add as many as you want to label
}

def get_source_bias(url):
    for domain, bias in SOURCE_BIAS.items():
        if domain in url:
            return(bias)
    return "undetermined"

