<template>
  <v-container>
    <v-row v-if="!loading">
      <!-- <transition name="col-transition"> -->
      <v-col cols="12" :md="paying ? 6 : 8" key="left-col" class="animate_07s">
        <AddressSelect :paying="paying" :addressPerPage="$vuetify.display.mdAndUp?3:($vuetify.display.xs?1:2)" :title="paying ? '地址信息' : '选择地址'"
          @updateSelectedAddress="updateSelectedAddress">

        </AddressSelect>

        <br>
        <v-card>
          <v-card-title>
            <h3>商品列表</h3>
          </v-card-title>
          <v-list>
            <v-list-item v-for="item in items" :key="item.item_id">
              <v-list-item-action class="d-inline-flex" style="width:100%">
                <v-img :src="item.image" height="96" width="96"></v-img>
                <v-container width="100%" style="margin-left: auto;">
                  <v-row>
                    <v-col cols="3" class="pt-0 ">
                      <strong>{{ item.product_name }}</strong>
                    </v-col>

                    <v-col cols="3" class="pt-0 text-center">
                      <a class="font-weight-bold text-decoration-none"
                        @click="router.push(`/shop/${getShopId(item.product_id)}`)">{{ getShopName(item.product_id)
                        }}</a>

                    </v-col>

                    <v-col cols="4" style="color:orangered" class="text-h6 pt-0 text-center">
                      {{ currency(item.price) }}
                    </v-col>

                    <v-col cols="2" class="text-center pt-0">
                      <b>x {{ item.quantity }}</b>

                    </v-col>
                  </v-row>

                </v-container>
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      <!-- </transition> -->
      <!-- <transition name="col-transition"> -->
      <v-col cols="12" :md="paying ? 6 : 4" key="right-col" class="animate_07s">
        <v-card style="position: sticky; top: 78px;" v-if="!paying">
          <v-card-title>
            <span class="font-weight-bold">本单合计 共 {{ quantityAll }} 件商品</span>
          </v-card-title>
          <v-list>
            <v-list-item v-for="item in items" :key="item.item_id">
              <v-container>
                <v-row>
                  <v-col cols="4" class="pt-0 ">
                    <strong>{{ item.product_name }}</strong>
                  </v-col>

                  <v-col cols="3" class="text-center pt-0">
                    <b>x {{ item.quantity }}</b>
                  </v-col>

                  <v-col cols="5" style="color:orangered" class="pt-0 text-right">
                    {{ currency(item.price) }}
                  </v-col>


                </v-row>
              </v-container>
            </v-list-item>
          </v-list>
          <v-card-text class="text-right" style="color:orangered;">
            合计：￥{{ cart.totalSum }}<br />
            优惠：{{ cart.discount }}<br />
            <span class="text-h5">实付：￥{{ cart.actualSum }}</span>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="router.push('/user/cart/')">返回修改</v-btn>
            <v-btn color="red-lighten-1" @click="checkout" class="font-weight-bold">立即下单</v-btn>
          </v-card-actions>
        </v-card>
        <v-card v-else>
          <v-card-title>
            <span class="font-weight-bold">支付订单</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="text-left">
            <div class="d-flex align-center">
              <span class="text-body-1">订单编号： &nbsp;&nbsp;</span>
              <v-chip color="primary">{{ orderIdList.join(', ') }}</v-chip><br />
            </div>
            <div class="mt-2">
              <span class="text-body-1">订单创建时间: {{ formatDate(orders[0].order_date) }}</span>


              <br />
            </div>
          </v-card-text>
          <v-card-text class="text-left" style="color:orangered">
            <div>
              <span class="text-h5">应付：￥{{ cart.actualSum }}元</span><br />
              <span class="text-h5">当前余额：￥{{ user.money }}元 </span>
                <v-btn @click="router.push('/user/profile/')" outlined class="text-primary" elevation="0">去充值</v-btn><br />
            </div>
            <br>
            <v-progress-linear indeterminate color="primary" v-if="waitingPayment"></v-progress-linear>
          </v-card-text>
          <v-card-actions>
            <v-btn block @click="pay" color="red-lighten-1" class="font-weight-bold text-body-1"
              :disabled="user.money < cart.actualSum"> {{ user.money < cart.actualSum?'余额不足，请充值':'确认支付' }}</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      <!-- </transition> -->
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { getAddresses, addAddress, profile } from '@/api/user';
import { cart } from '@/store/cart';
import { user } from '@/store/user';
import { useRouter } from 'vue-router';
import snackbar from '@/api/snackbar'; ``
import { getShopInfo } from '@/api/shop';
import { getProductDetail } from '@/api/product';
import { createOrder, userPayOrders } from '@/api/order';
import AddressSelect from '@/components/addressSelect.vue';



function formatDate(dateStr) {
  const date = new Date(dateStr);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${year}年${month}月${day}日 ${hour}:${min}:${seconds}`;
}

const loading = ref(true);
const router = useRouter();
const items = ref([]);

const currency = (value) => {
  let val = parseFloat(value);
  if (val > 9999999) {
    return `￥${(val / 10000).toFixed(2)} 万`;
  } else {
    return `￥${parseFloat(value).toFixed(2)}`;
  }
};

const fetchOrderItems = async () => {
  if (cart.selectedItems.length === 0) {
    snackbar.error("您还未选中商品");
    router.push('/user/cart/');
    return;
  }
  items.value = cart.selectedItems;
  for (const item of items.value) {
    await shopInfo(item);
  }
  loading.value = false;
};

const quantityAll = computed(() => {
  return cart.selectedItems.reduce((acc, item) => acc + item.quantity, 0);
});

/*

地址相关

*/
const updateSelectedAddress = (newAddress) => {
  selectedAddress.value = newAddress;
};

const selectedAddress = ref(null);

// shopInfo

const shopInfoCache = {};
const product_shop = {};

const shopInfo = async (product) => {
  let productId = product.product_id;
  const shopId = (await getProductDetail(productId)).data.shop;
  if (!shopInfoCache[shopId]) {
    const response = await getShopInfo(shopId);
    shopInfoCache[shopId] = response;
  }
  product_shop[productId] = shopId;
  return shopInfoCache[shopId];
};

const getShopName = (productId) => {
  const shopId = product_shop[productId];
  return shopInfoCache[shopId].name;
};

const getShopId = (productId) => {
  return product_shop[productId];
};

const paying = ref(false);
const orderIdList = ref([]);
const orders = ref([]);
const waitingPayment = ref(false);

onMounted(() => {

  // fetchAddresses();
  fetchOrderItems();
});

const checkout = async () => {
  if (!selectedAddress.value) {
    snackbar.error("请选择地址");
    return;
  }
  const addressId = selectedAddress.value.id;
  const items = cart.selectedItems.map(item => {
    return {
      "product_id": item.product_id,
      "quantity": item.quantity
    };
  });
  let data = {
    address_id: addressId,
    items: items
  };
  //console.log(data);
  const response = await createOrder(data);
  if (response.success) {
    snackbar.success("下单成功");
    await profile();
    paying.value = true;
    //console.log(response.data.orders);
    orders.value = response.data.orders;
    cart.selectedItems = [];
    orderIdList.value = response.data.orders.map(order => order.order_id);
    //console.log(orderIdList.value);
  } else {
    snackbar.error("下单失败");
    console.log(addressId);
  }
};

const pay = async () => {
  const response = await userPayOrders(orderIdList.value);
  waitingPayment.value = true;
  if (response.success) {
    await new Promise(resolve => setTimeout(resolve, 1500));
    snackbar.success("支付成功");
    waitingPayment.value = false;
    await new Promise(resolve => setTimeout(resolve, 500));
    router.push('/order/');
  } else {
    snackbar.error("支付失败");
  }
}

</script>

<style scoped>
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* 隐藏 Firefox 中的上下增减按钮 */
input[type="number"] {
  -moz-appearance: textfield;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.5s ease, opacity 0.5s ease;
}

.slide-left-enter,
.slide-left-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.5s ease, opacity 0.5s ease;
}

.slide-right-enter,
.slide-right-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

.animate_07s {
  transition: all 0.7s ease-in-out;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>