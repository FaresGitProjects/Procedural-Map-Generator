# code to be profiled
profile.run("main()", "profile")

# generate report
p = pstats.Stats("profile")
p.strip_dirs().sort_stats("time").print_stats()