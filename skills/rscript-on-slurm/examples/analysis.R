args <- commandArgs(trailingOnly = TRUE)
output_dir <- if (length(args) >= 1) args[[1]] else "results"

dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

message("R version: ", getRversion())
message("R_LIBS_USER: ", Sys.getenv("R_LIBS_USER", unset = "<unset>"))
message("Library paths:")
print(.libPaths())
message("Session info:")
print(sessionInfo())

set.seed(1)
values <- data.frame(
  x = seq_len(10),
  y = cumsum(rnorm(10))
)

csv_path <- file.path(output_dir, "rscript-demo.csv")
summary_path <- file.path(output_dir, "rscript-summary.txt")

write.csv(values, csv_path, row.names = FALSE)
writeLines(
  c(
    "Rscript demo complete",
    paste("rows:", nrow(values)),
    paste("mean_y:", round(mean(values$y), 6))
  ),
  summary_path
)

message("Wrote: ", csv_path)
message("Wrote: ", summary_path)
