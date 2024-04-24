// Top-level functions
fun main() {}


// Generic functions
fun <T> test() {}


// Generic functions with parameters
fun <T: Int> bar(foo: Int): T {}


// Functions with parameters
fun main(args: Array<String>) {}
fun sum(a: Int, b: Int) = a + b


// Functions with return types
fun answerToTheUltimateQuestionOfLifeTheUniverseAndEverything(): Int = 42


// Functions with return calls
fun foo(p0: Int): Long {
  return p0.toLong()
}


// Override functions
override fun boo() = foo()


// Function with backticked name
fun `this is a test function`() = true


// Function with few modifiers (access and other)
private inline fun readTypeAlias(
    typeAliasProto: ProtoBuf.TypeAlias,
    packageName: CirPackageName,
    strings: NameResolver,
    types: TypeTable,
    consumer: (CirEntityId, CirProvided.Classifier) -> Unit
) {
    val typeAliasId = CirEntityId.create(packageName, CirName.create(strings.getString(typeAliasProto.name)))

    val typeParameterNameToIndex = HashMap<Int, Int>()
    val typeParameters = readTypeParameters(
        typeParameterProtos = typeAliasProto.typeParameterList,
        typeParameterIndexOffset = 0,
        nameToIndexMapper = typeParameterNameToIndex::set
    )

    val underlyingType = readType(typeAliasProto.underlyingType(types), TypeReadContext(strings, types, typeParameterNameToIndex))
    val typeAlias = CirProvided.TypeAlias(typeParameters, underlyingType as CirProvided.ClassOrTypeAliasType)

    consumer(typeAliasId, typeAlias)
}


// Test function
fun test(a: Inv<A>, b: Inv<B>) {
    val intersectionType = intersection(a, b)

    use(intersectionType) { intersectionType }
    useNested(intersectionType) { Inv(intersectionType) }

    var d by createDelegate { intersectionType }
}

@Test
fun testSum() {
    val expected = 42
    assertEquals(expected, testSample.sum(40, 2))
}
