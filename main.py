from LawSemAnalyser.SemAnalyser import SemAnalyser

# SemAnalyser("ścieżka/do/folderu/wyjściowego", "ścieżka/do/folderu/wejściowego")
analyser = SemAnalyser("out", "prawo_konsumenckie_html")
analyser.analyseDocs()