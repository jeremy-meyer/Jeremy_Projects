
//4 Different IDs
//spark.read.parquet("/stream/supersensor/data/2018-06-07/1340/*").select($"id").distinct.show. Old file
sc.applicationId
val sample = spark.read.parquet("/stream/supersensor/data/2018-06-07/2100/*")
sample.select($"id").distinct.show

//Structure of Dataset
sample.printSchema

//Labels: For future reference
//val labels = spark.read.parquet("/stream/supersensor/labels/2018-06-07/2100/*")
//labels.toJSON.take(2)
//labels.select("value").show(false)

//Just to see how selecting works
import org.apache.spark.sql.functions._
sample.select($"id", $"data.*").sort(desc("milliseconds")).filter($"id" === "a42a88c400d7").show(10)

//We'll only take 1 ID for the sample. Data needed to be ordered by time stamp
val id42 = sample.select($"id", $"data.*").filter($"id" === "a42a88b8008c").orderBy($"milliseconds")
id42.show(10)

//Concatenation. What do I need to concatenate? Come back to this
import org.apache.spark.sql.functions.{concat, lit}
id42.select(concat($"id", lit(" "), $"milliseconds").alias("Conc")).show(false)

//Normalizing Time
import org.apache.spark.sql.functions.{min, max}

//val m = id42.agg(min("milliseconds")).head.getInt(0)
val m = id42.select($"milliseconds").head.getLong(0)
val id42Acc = id42.select($"milliseconds" - m as "TimeNorm", $"accelerometerSensor")

//Trying to filter out the empty lists, but having trouble

id42Acc.show(10, false)
//val t = id42Acc.select($"accelerometerSensor").filter($"accelerometerSensor".getList(0).size != 0)
val t = id42Acc.select($"accelerometerSensor").first.getList(0).size

val id42Mic = id42.select($"milliseconds" - m as "TimeNorm", $"memMic")
id42Mic.show()

id42Mic.select($"memMic").head(3)(2).getClass

//id42Mic.filter($"memMic".isEmpty)
import scala.collection.mutable
def cellSize(cell: Any): Double = {
    return(cell.getList(0).size)
}

//FFT in scala
%AddDeps org.scalanlp breeze_2.12 0.13.2
import breeze.linalg._
import breeze.signal._
import breeze.numerics._
import breeze.math._


def FFTRec(wave: DenseVector[Double], thresh: Double = .2, f_s: Double = 100): DenseMatrix[Double] = {
    def npHanning(M:Int): DenseVector[Double] = {
        val n = DenseVector((0.0 to (M.toDouble-1) by 1).toArray)
        return 0.5 - 0.5*cos(2.0*Pi*n / (M.toDouble-1))
    }

    val win = npHanning(wave.size)
    val FFT = fourierTr(win * wave)
    val n = FFT.size
    val freq_hanned = fourierFreq(n, f_s)
    val half_n = ceil(n/2.0).toInt
    val fft_hanned_half = FFT.slice(0,half_n) *:* Complex(4.0/n, 0)
    val freq_hanned_half = freq_hanned.slice(0,half_n)
    val amps = abs(fft_hanned_half)

    def locMax(ts :DenseVector[Double], thresh: Double = 0.3): DenseVector[Int] = {
        var maxs: Array[Int] = Array()
        for( i <- 1 to ts.size-2){
            if(ts(i) - ts(i-1) > thresh && ts(i) - ts(i+1) > thresh){
                maxs = maxs ++ Array(i)
            }
        }
        return DenseVector(maxs)
    }
    
    val max_freqs_ind = locMax(amps, thresh)
    val w_found = max_freqs_ind.size
    var freqs_found = DenseVector.zeros[Double](w_found)
    var amps_found = DenseVector.zeros[Double](w_found)
    for(i <- 0 to w_found-1){
        freqs_found(i) = freq_hanned_half(max_freqs_ind(i))
        amps_found(i) = amps(max_freqs_ind(i))
    }
    return(DenseMatrix.vertcat(freqs_found.toDenseMatrix, amps_found.toDenseMatrix))
}


