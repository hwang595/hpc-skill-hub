cwlVersion: v1.2
class: CommandLineTool
baseCommand: wc
stdout: line-count.txt

inputs:
  input_file:
    type: File
    inputBinding:
      position: 2

arguments:
  - position: 1
    valueFrom: -l

outputs:
  line_count:
    type: File
    outputBinding:
      glob: line-count.txt
