from pyo import *


class MiniMoog(PyoObject):
    """
    3 OSC subractive synthesizer, whith moog style fourth-order resonant lowpass filter, ADSR, FILTER ENVELOPE and external FX (delay, reverb).
    You can control the TUNE, OSC PARAMETERS, FILTER, ADSR, FILTER ENVELOPE via GUI
    Drone mode (envelope off) in progress...
    :Parent: :py:class:`PyoObject`
    :Args:

      detune : int, optional
          Modify all OSC tuning

      wave1 : int, optional
          Waveform type of OSC1. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated Sine
            Default to 0.
      wave2 : int, optional
          Waveform type of OSC2. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated 
            Default to 0.
     wave3 : int, optional
          Waveform type of OSC3. Eight possible values : 
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated Sine
            Default to 0.
      octave_n: int, optional
          Tune OSC_N to a new octave. Four possible values : +1,+2,+3,+4

      cutoff: int, optional
          Filter cutoff position, default to 20000hz
      res: int, optional
          filter resonance, defaulto to 0
      delaytime: int, optional
          control the delay time, default to 0s
      revsize: int, optional
          control the rev decay time, default to 0s

      
    >>> s=Server().boot()
    >>> moog = MiniMoog().out()
    >>> moog.ctrl()
    """


    def __init__(self, wave1=1, wave2=1, wave3=1, delaytime=0, revsize=0, mul=20):

        super().__init__()

        #control signals
        self._detune =  Sig(1)
        self._octave1 = Sig(1)
        self._octave2 = Sig(1)
        self._octave3 = Sig(1)
        self._cutoff= Sig(1)
        self._res= Sig(1)
        

        #osc attribute
        self._wave1= wave1
        self._wave2= wave2
        self._wave3= wave3


        

        #delay and reverb attribute
        self._delaytime= delaytime
        self._revsize= revsize
        

        #note input
        
        notes = Notein()
        notes.keyboard()
        freq = MToF(notes["pitch"])

       

        #volume envelope
        self._env1 = MidiAdsr(notes["velocity"], attack=0.005, decay=0.1, sustain=0.7, release=0.5, mul=0.1)
        #filter envelope
        self._env2 = MidiAdsr(notes["velocity"], attack=0.005, decay=0.1, sustain=0.7, release=0.5, mul=0.1)

        self._osc1= OSC(freq=(freq * self._octave1)+ self._detune*5, type=self._wave1, mul=self._env1)
        self._osc2= OSC(freq=(freq * self._octave2)+ self._detune*5, type=self._wave2, mul=self._env1)
        self._osc3= OSC(freq=(freq * self._octave3)+ self._detune*5, type=self._wave3, mul=self._env1)
        #audio processing
        self._mixer = self._osc1 + self._osc2 + self._osc3
        self._filter = MoogLP(self._mixer,freq=self._cutoff*self._env2, res=self._res) 
        self._pan = Pan(self._filter, outs=2, pan=.5 )
        self._delay=Delay(self._pan,delay=self._delaytime)
        self._reverb= Freeverb(self._delay, size=self._revsize)
        self._amp= (self._reverb * self._mul)+ self._add
        
       

        
        #declared output
        self._base_objs = self._amp.getBaseObjects()



    def ctrl(self, map_list=None, title=None, wxnoserver=False):

        #signal control 
        detmap=SLMap(-20,20,"lin", "value",0)
        octmap=SLMap(1,4,"lin", "value",1,res='int')
        cuttmap=SLMap(1,20000,"lin", "value",20000)
        resmap=SLMapQ()
        mulmap=SLMapMul(init=2)
        
        self._detune.ctrl([detmap], title="Tune control")
        self._octave1.ctrl([octmap], title="Octave control 1")
        self._octave2.ctrl([octmap], title="Octave control 2")
        self._octave3.ctrl([octmap], title="Octave control 3")
        self._cutoff.ctrl([cuttmap], title="filter control ")
        self._res.ctrl([resmap], title="resonance control ")
        self._amp.ctrl([mulmap], title="Amp control")
        
        
        self._osc1.ctrl()
        self._osc2.ctrl()
        self._osc3.ctrl()
        
    

        
        self._env1.ctrl(title="ADSR")
        self._env2.ctrl(title="Filter ENV")
        

        
        
        self._delay.ctrl()
        self._reverb.ctrl()
       
        




    def play(self, dur=0, delay=0):
        self._detune.play(dur, delay)
        self._octave1.play(dur, delay)
        self._octave2.play(dur, delay)
        self._octave3.play(dur, delay)
        self._osc1.play(dur, delay)
        self._osc2.play(dur, delay)
        self._osc3.play(dur, delay)
        self._octave1.play(dur, delay)
        self._octave2.play(dur, delay)
        self._octave3.play(dur, delay)
        self._filter.play(dur, delay)
        self._pan.play(dur, delay)
        return super().play(dur, delay)

    def stop(self):
        self._osc1.stop()
        self._osc2.stop()
        self._osc3.stop()
        self._octave1.stop()
        self._octave2.stop()
        self._octave3.stop()
        self._dronemod.stop()
        self._filter.stop()
        self._pan.stop()
        return super().stop()

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._osc1.play(dur, delay)
        self._osc2.play(dur, delay)
        self._osc3.play(dur, delay)
        self._filter.play(dur, delay)
        self._pan.play(dur, delay)
        return super().out(chnl, inc, dur, delay)

    #osc methods

    def setDetune(self, x):
        """
        Replace the `octave1` attribute.

        """
        self._detune = Sig(x)

    def setOctave1(self, x):
        """
        Replace the `octave1` attribute.

        """
        self._octave1 = Sig(x)

    def setOctave2(self, x):
        """
        Replace the `octave2` attribute.

        """
        self._octave2 = Sig(x)

    def setOctave3(self, x):
        """
        Replace the `octave3` attribute.

        """
        self._octave3 = Sig(x)
        
    def setWave1(self, x):
        """
        Replace the `wave1` attribute.

        """
        self._wave1 = x
        self._osc1.type = x

    def setWave2(self, x):
        """
        Replace the `wave2` attribute.

        """
        self._wave2 = x
        self._osc1.type = x

    def setWave3(self, x):
        """
        Replace the `wave3` attribute.

        """
        self._wave1 = x
        self._osc1.type = x

    #filter methods
    def setFreq(self, x):
        """
        Replace the `cutoff` attribute.
        :Args:
            x : float or PyoObject
                New `cutoff` attribute.
        """
        self._cutoff = Sig(x)
        self._filter.freq = x
    
    def setRes(self, x):
        """
        Replace the `res` attribute.
        :Args:
            x : float or PyoObject
                New `res` attribute.
        """
        self._res = Sig(x)
        self._filter.res = x

    #delay, reverb methods

    def setTime(self, x):
        """
        Replace the `delay` attribute.
        :Args:
            x : float or PyoObject
                New `cutoffFact` attribute.
        """
        self._delaytime= x
        self._delay.delay = x

    def setSize(self, x):
        """
        Replace the `size` attribute.
        :Args:
            x : float or PyoObject
                New `cutoffFact` attribute.
        """
        self._revsize= x
        self._reverb.size= x


    #property and setter
    @property
    def detune(self):
        """int. detune value."""
        return self._detune
    @detune.setter
    def wave11(self, x):
        self.setDetune(x)
    @property
    def octave1(self):
        """int. octave1 value."""
        return self._octave1
    @octave1.setter
    def octave1(self, x):
        self.setOctave1(x)
    @property
    def octave2(self):
        """int. octave2 value."""
        return self._octave2
    @octave2.setter
    def octave2(self, x):
        self.setOctave2(x)
    @property
    def octave3(self):
        """int. octave3 value."""
        return self._octave3
    @octave3.setter
    def octave3(self, x):
        self.setOctave3(x)

    @property
    def wave1(self):
        """int. Type of osc1."""
        return self._wave1
    @wave1.setter
    def wave1(self, x):
        self.setWave1(x)
    
    @property
    def wave2(self):
        """int. Type of osc2."""
        return self._wave2
    @wave2.setter
    def wave2(self, x):
        self.setWave2(x)

    @property
    def wave3(self):
        """int. Type of osc3."""
        return self._wave3
    @wave3.setter
    def wave3(self, x):
        self.setWave3(x)

    @property
    def cutoff(self):
        """float or PyoObject. CutoffFact of filt."""
        return self._cutoff
    @cutoff.setter
    def cutoff(self, x):
        self.setCutoff(x)

    @property
    def res(self):
        """float or PyoObject. Res of filt."""
        return self._res
    @res.setter
    def res(self, x):
        self.setRes(x)

    @property
    def delaytime(self):
        """float or PyoObject. delaytime."""
        return self._delaytime
    @delaytime.setter
    def delaytime(self, x):
        self.setTime(x)

    @property
    def revsize(self):
        """float or PyoObject. reverb size."""
        return self._revsize
    @revsize.setter
    def revsize(self, x):
        self.setSize(x)
        




#CUSTOM OSC CLASS
class OSC(PyoObject):

    def __init__(self, freq=100, sharp=0.5, type=0, mul=1, add=0):
        pyoArgsAssert(self, "OOiOO", freq, sharp, type, mul, add)
        PyoObject.__init__(self, mul, add)
        self._freq = freq 
        self._sharp = sharp
        self._type = type
        freq, sharp, type, mul, add, lmax = convertArgsToLists(freq, sharp, type, mul, add)
        self._base_objs = [
            LFO_base(wrap(freq, i), wrap(sharp, i), wrap(type, i), wrap(mul, i), wrap(add, i)) for i in range(lmax)
        ]
        self._init_play()

        

    def setFreq(self, x):
        
        pyoArgsAssert(self, "O", x)
        self._freq = x 
        x, lmax = convertArgsToLists(x)
        [obj.setFreq(wrap(x, i)) for i, obj in enumerate(self._base_objs)]


    def setSharp(self, x):
       
        pyoArgsAssert(self, "O", x)
        self._sharp = x
        x, lmax = convertArgsToLists(x)
        [obj.setSharp(wrap(x, i)) for i, obj in enumerate(self._base_objs)]


    def setType(self, x):
        
        pyoArgsAssert(self, "i", x)
        self._type = x
        x, lmax = convertArgsToLists(x)
        [obj.setType(wrap(x, i)) for i, obj in enumerate(self._base_objs)]


    def reset(self):
        
        [obj.reset() for i, obj in enumerate(self._base_objs)]

    #mul and sharp deleted
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(0.1, self.getSamplingRate() * 0.25, "log", "freq", self._freq),
            SLMap(0, 7, "lin", "type", self._type, "int", dataOnly=True),

            SLMapMul(self._mul),
        ]
        PyoObject.ctrl(self, map_list, title, wxnoserver)


    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, x):
        self.setFreq(x)

    @property
    def sharp(self):
        return self._sharp

    @sharp.setter
    def sharp(self, x):
        self.setSharp(x)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, x):
        self.setType(x)




        

        
        
    


if __name__ == "__main__":

    s=Server().boot()
    s.amp=0.5
    s.setMidiInputDevice(99)

    moog = MiniMoog()
    moog.ctrl()
    moog.out()
    Scope(moog)
    
    s.gui(locals())     



