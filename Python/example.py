from LawSemAnalyser import SemAnalyser

# SemAnalyser("ścieżka/do/folderu/wyjściowego", "ścieżka/do/folderu/wejściowego")
analyser = SemAnalyser("out", "example_html")
analyser.analyse_docs()