version 1.1

workflow wordcount {
  input {
    File input_file
  }

  call count_lines {
    input:
      input_file = input_file
  }

  output {
    File line_count = count_lines.line_count
  }
}

task count_lines {
  input {
    File input_file
  }

  command <<<
    wc -l ~{input_file} > line-count.txt
  >>>

  output {
    File line_count = "line-count.txt"
  }

  runtime {
    cpu: 1
    memory: "512 MiB"
  }
}
