# essas duas linhas configuram o R pra pegar os binários dos pacotes a partir do repositório da Posit
# pra evitar compilação, que desperdiça MUITO tempo
options(HTTPUserAgent = sprintf("R/%s R (%s)", getRversion(), paste(getRversion(), R.version["platform"], R.version["arch"], R.version["os"])))
options(repos = c(CRAN = "https://packagemanager.posit.co/cran/__linux__/noble/latest"))
# permite ao script usar múltiplos núcleos para acelerar a execução
options(Ncpus = parallel::detectCores())



# Bibliotecas necessárias para o projeto
pacotes = c("dplyr", "lubridate", "stringr", "stringi", "ggplot2", "here", "ISOcodes")

# Biblioteca pessoal (evita erro de permissão em /usr/local/lib/R/site-library)
lib_pessoal = Sys.getenv("R_LIBS_USER")
if (lib_pessoal == "") lib_pessoal = file.path(Sys.getenv("HOME"), "R", "library")
dir.create(lib_pessoal, showWarnings = FALSE, recursive = TRUE)
.libPaths(c(lib_pessoal, .libPaths()))
 
faltantes = setdiff(pacotes, rownames(installed.packages()))
if (length(faltantes) > 0) {
  # repos explícito: no Rscript (não interativo) o R não pergunta o espelho do CRAN
  install.packages(faltantes, lib = lib_pessoal, repos = "https://cloud.r-project.org")
}
