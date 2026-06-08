using Dates
using InteractiveUtils
using Statistics

output_dir = length(ARGS) >= 1 ? ARGS[1] : "results"
mkpath(output_dir)

println("Julia version: ", VERSION)
println("Timestamp UTC: ", Dates.format(now(UTC), dateformat"yyyy-mm-ddTHH:MM:SSZ"))
println("JULIA_DEPOT_PATH: ", get(ENV, "JULIA_DEPOT_PATH", "<unset>"))
println("JULIA_PROJECT: ", get(ENV, "JULIA_PROJECT", "<unset>"))
println("Threads.nthreads(): ", Threads.nthreads())

println("DEPOT_PATH:")
foreach(path -> println(" - ", path), DEPOT_PATH)

println("LOAD_PATH:")
foreach(path -> println(" - ", path), LOAD_PATH)

println("versioninfo:")
versioninfo()

values = cumsum(randn(10))
csv_path = joinpath(output_dir, "julia-demo.csv")
summary_path = joinpath(output_dir, "julia-summary.txt")

open(csv_path, "w") do io
    println(io, "x,y")
    for (index, value) in enumerate(values)
        println(io, index, ",", value)
    end
end

open(summary_path, "w") do io
    println(io, "Julia demo complete")
    println(io, "rows: ", length(values))
    println(io, "mean_y: ", round(mean(values), digits = 6))
    println(io, "threads: ", Threads.nthreads())
end

println("Wrote: ", csv_path)
println("Wrote: ", summary_path)
