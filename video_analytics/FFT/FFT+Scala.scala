
//Adding Scala Library

%AddDeps org.scalanlp breeze_2.12 0.13.2
//%AddDeps org.scalanlp breeze-viz_2.12 0.13.2
sc.applicationId
import breeze.linalg._
val x = DenseVector.zeros[Double](5)

//Initiating variabules and creating the test wave

import breeze.signal._
import breeze.numerics.constants.Pi
import breeze.numerics.{sin, cos}

val f_s = 100.0 // Hz  sampling frequency OR #records/1 sec
val f = 1.0
val tFqs = DenseVector(11.0,24.0,17.0)
val tAmps = DenseVector(5.1,-3.5, .5)
val time = DenseVector((0.0 to 10.0 by 1/f_s).toArray)

def createWave(fqs: DenseVector[Double], amps: DenseVector[Double], f_s: Double = 100, f:Double = 1.0): DenseVector[Double] = {
    var w = DenseVector(breeze.stats.distributions.Gaussian(0, 1).sample(time.size).toArray) //White Noise
    for (i <- Range(0, amps.size)){
        w += amps(i) * sin(fqs(i) * 2 * Pi * f * time)
    }
return w
}
val wave = createWave(tFqs, tAmps)


//FFT wave data and compute recovered frequencies/amplitudes

import breeze.signal._
import breeze.numerics._
import breeze.math._

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

val max_freqs_ind = locMax(amps, .5/3)
val w_found = max_freqs_ind.size
var freqs_found = DenseVector.zeros[Double](w_found)
var amps_found = DenseVector.zeros[Double](w_found)
for(i <- 0 to w_found-1){
    freqs_found(i) = freq_hanned_half(max_freqs_ind(i))
    amps_found(i) = amps(max_freqs_ind(i))
}

//Return DenseMatrix.vertcat(freqs_found.toDenseMatrix, amps_found.toDenseMatrix)

printf("Recovered # of Waves:   %s\n", w_found)
printf("True # of Waves:        %s\n", tFqs.size)
printf("Recovered Frequencies:  %s\n", freqs_found)
printf("True Frequencies:       %s\n", tFqs)
printf("Recovered Amplitudes :  %s\n", amps_found)
printf("True Amplitudes:        %s\n", tAmps)


//Function that returns a matrix of the frequencies/amplitudes for convience. 

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

//One-line test. Assumes f_s=100
print(FFTRec(createWave(DenseVector(10.0,17.0,39.0), DenseVector(-3.0,5.1,20.0)))) //Frequencies, then amplitudes


//Plots don't seem to work
//import breeze.plot._
//val fig = Figure()
//val plt = fig.subplot(0)
//plt += plot(freq_hanned_half, amps)
