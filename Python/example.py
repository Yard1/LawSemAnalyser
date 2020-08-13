from LawSemAnalyser import SemAnalyser

# SemAnalyser("ścieżka/do/folderu/wyjściowego", "ścieżka/do/folderu/wejściowego")
analyser = SemAnalyser("../out", "../prawo_konsumenckie_html", docker_image=None)
analyser.analyse_docs()