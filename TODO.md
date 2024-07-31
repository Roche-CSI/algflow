# TODO
- [ ] Asset Integration
- [ ] Reusable Algorithm

##### Transforms
In 'Algflow', a transform is almost same as algorithms except for its inputs/outputs. The `Algorithm` 
has named inputs and outputs, while transform inputs and outputs are positional. An example of the
transform is given below:

```python3
from algflow import Transform
class TempStat(Transform):
    class Input:
        data =
    class Output:
        mean =
        median = 
        variance = 
    
    
class SortCell(PrefixTransform):
    prefix = "sorted_"
    def runs(self, input):
        # code to transform
        ...
        ...
        output = ...
        return output

class NormalizeCell(Algorithm):
    class Input:
        sorted_cells = Array(dtype=np.float32) # automatically resolves to input = cells and output = sorted_cells
        avg_tem = Array(pipeline="chip_temp|TempStat|[mean]") # reusing normal algorithm

```

- [ ] Input/Output Interface Abstraction
- [ ] Output Query Language
- [ ] Algflow Runner ( Local )
- [ ] Algflow based steps in Annotator
- [ ] Algflow 
- [ ] Parallelizer ( Local )
- [ ] Parameters Obsolescence
- [ ] Dynamic pipelines ( yield Algorithm from another Algorithm)

# Input Abstraction
Algflow abstracts the source of inputs such as `csv`, `hdf5`, `parquet` and provides a `named` 
inputs to algorithms. This makes `Algorithm` abstraction to support multiple input sources without 
any changes to the algorithm. The input handlers are implemented as plugins which enables additional 
input sources in the future.

In order to aid in the construction of the `DAG`, the algflow requires the following interface 
to be implemented by plugins:

- `input_types` - The kind of inputs the plugin can handle. This is a list of 
  (extension, content_type) pairs.
- `inputs` - The name and properties of inputs available from the source handled by the plugin.
   Each input will defined the following properties:
  - name - input name
  - type - input type
  - shape - dimension of the input if it's a vector
  - meta - Any meta information about the input which can help creation of `DAG` or help optimize 
    the pipeline

# H5 Plugin
  The handler will need the following info block:
   - name
   - dim (0, 1, 2, 3, 4)
   - type (np.int32, int64, object)
   - shape ( x, y, z, ) ( 2000, '*')




