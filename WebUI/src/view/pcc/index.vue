<template>
  <div>

  <van-nav-bar title="PCC x64 WebUI" />
<van-cell value="A PCC online playground. You can test your code here or run some test_cases." />
<van-divider> Generate ASM code </van-divider>
<van-cell>
You can derive test cases from here.
<a href="https://github.com/chengsyuan/PCC/tree/master/test_case">https://github.com/chengsyuan/PCC/tree/master/test_case</a>
</van-cell>



  <van-cell-group>
  <van-field
    v-model="ccode"
    rows="3"
    autosize
    label="PCC Code"
    type="textarea"
    placeholder="Type your C code here, or select from demos!"
    maxlength="999999"
    show-word-limit
  >
  <van-button slot="button" size="large" type="primary" @click="compile">Compile</van-button>
  </van-field>
</van-cell-group>


<van-divider> Assemble & Link the code </van-divider>
  <van-cell-group>
  <van-field
    v-model="asmcode"
    rows="10"
    label="ASM Code"
    type="textarea"
    placeholder="Please compile first!"
    maxlength="999999"
    show-word-limit
  >
  <van-button slot="button" size="large" type="primary" @click="link">GenObj&Link</van-button>
  </van-field>
</van-cell-group>


<van-divider> Run your program </van-divider>

  <van-cell-group>
  <van-field
    v-model="input"
    rows="3"
    autosize
    label="Input"
    type="textarea"
    placeholder="Text your input here, default is no input!"
    maxlength="999999"
    show-word-limit
  >
  <van-button slot="button" size="large" type="primary" @click="run">Run!</van-button>
  </van-field>
</van-cell-group>

  <van-cell-group>
  <van-field
    v-model="output"
    rows="10"
    label="Output"
    type="textarea"
    placeholder="Click run to get the output!"
    maxlength="999999"
    show-word-limit
  ></van-field>
</van-cell-group>

<van-divider> About </van-divider>
<van-cell value="PCC x86 is my compilation coursework and I would appreciate my instructor Weihong, Yao for her valuable suggestions and also credit to Wenyu, Xing" />

  </div>
</template>

<script>
import { Row, Col, Icon, Cell, CellGroup, Field, NavBar , Button , Divider , Dialog} from 'vant';
import axios from 'axios';

export default {
  components: {
    [Row.name]: Row,
    [Col.name]: Col,
    [Icon.name]: Icon,
    [Cell.name]: Cell,
    [CellGroup.name]: CellGroup,
    [Field.name]: Field,
    [NavBar.name]: NavBar,
    [Button.name]: Button,
    [Divider.name]: Divider,
    [Dialog.name]: Dialog,
  },data() {
    return {
      ccode : '',
      asmcode : '',
      input: '',
      output: '',
    }
  },methods: {
    compile(){
      const postData = {
        src : this.ccode
      };
      var self=this;
      var url = 'api/compile';
      axios.post(url,postData).then(function (res) {
        //console.log(res.data);
        var ret = res.data;

        Dialog.alert({
          message: ret['msg']
        }).then(() => {
          
        });
        self.asmcode = ret['asm'];
      }).catch(function (error) {
          console.log(error);
      });

    },
    link(){
      const postData = {
        src : this.ccode
      };
      var self=this;
      var url = 'api/link';
      axios.post(url,postData).then(function (res) {
        console.log(res.data);
        var ret = res.data;

        Dialog.alert({
          message: ret['msg']
        }).then(() => {
          
        });
      }).catch(function (error) {
          console.log(error);
      });

    },
    run(){
      const postData = {
        input : this.input
      };
      var self=this;
      var url = 'api/run';
      axios.post(url,postData).then(function (res) {
        console.log(res.data);
        var ret = res.data;

        Dialog.alert({
          message: ret['msg']
        }).then(() => {
          
        });
        self.output = ret['output'];
      }).catch(function (error) {
          console.log(error);
      });

    },
  }
};
</script>

<style lang="less">


</style>
